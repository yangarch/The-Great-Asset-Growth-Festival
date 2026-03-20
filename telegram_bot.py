#!/usr/bin/env python3
"""
Telegram bot that accepts code modification requests
and applies them to the project via Claude Code CLI,
then commits and pushes to git.
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.resolve()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]


def is_authorized(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        return True  # 설정 없으면 모두 허용 (개발 단계)
    return user_id in ALLOWED_USER_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    await update.message.reply_text(
        "안녕하세요! 코드 수정 요청을 보내주세요.\n"
        "예: '자산 데이터 조회 API에 페이지네이션 추가해줘'\n\n"
        "명령어:\n"
        "/start - 도움말\n"
        "/status - git 상태 확인\n"
        "/log - 최근 커밋 로그"
    )


async def git_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip() or "변경사항 없음 (clean)"
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


async def git_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip() or "커밋 없음"
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


def run_claude(prompt: str) -> tuple[str, bool]:
    """Claude Code CLI를 실행하고 (출력, 성공여부)를 반환."""
    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", prompt],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
            stdin=subprocess.DEVNULL,  # 터미널 stdin 격리
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            error = result.stderr.strip()
            return f"Claude 실행 오류:\n{error}", False
        return output, True
    except subprocess.TimeoutExpired:
        return "타임아웃: 요청이 5분을 초과했습니다.", False
    except FileNotFoundError:
        return "오류: `claude` CLI가 설치되어 있지 않습니다.", False


def git_commit_and_push(commit_message: str) -> tuple[str, bool]:
    """변경된 파일을 커밋하고 push."""
    # 변경사항 확인
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        return "변경사항 없음 - 커밋 스킵", False

    # git add
    subprocess.run(["git", "add", "-A"], cwd=PROJECT_DIR, check=True)

    # git commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    if commit_result.returncode != 0:
        return f"커밋 실패:\n{commit_result.stderr.strip()}", False

    # git push
    push_result = subprocess.run(
        ["git", "push"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    if push_result.returncode != 0:
        return f"Push 실패:\n{push_result.stderr.strip()}", False

    return "커밋 & Push 완료", True


def split_message(text: str, max_length: int = 4000) -> list[str]:
    """텔레그램 메시지 길이 제한(4096자) 대응."""
    if len(text) <= max_length:
        return [text]
    parts = []
    while text:
        parts.append(text[:max_length])
        text = text[max_length:]
    return parts


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return

    user_request = update.message.text.strip()
    if not user_request:
        return

    await update.message.reply_text("⏳ Claude Code 실행 중... (최대 5분 소요)")

    # Claude Code 실행
    loop = asyncio.get_event_loop()
    claude_output, success = await loop.run_in_executor(None, run_claude, user_request)

    if not success:
        await update.message.reply_text(f"실패:\n{claude_output}")
        return

    # Claude 응답 전송 (길면 분할)
    for part in split_message(claude_output):
        await update.message.reply_text(part)

    # git commit & push (변경사항 있을 때만 알림)
    commit_msg = f"[telegram] {user_request[:72]}"
    git_result, committed = await loop.run_in_executor(
        None, git_commit_and_push, commit_msg
    )

    if committed:
        await update.message.reply_text(f"✅ {git_result}")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN 환경변수가 설정되어 있지 않습니다.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", git_status))
    app.add_handler(CommandHandler("log", git_log))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("봇 시작됨 (프로젝트: %s)", PROJECT_DIR)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
