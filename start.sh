#!/usr/bin/env bash
# =============================================================================
# start.sh — 充电站净利润风险仿真系统一键启动脚本
# 用法：bash start.sh
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_PORT=8000
FRONTEND_PORT=5500

# ── 颜色输出 ─────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()   { echo -e "${GREEN}[ OK ]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR ]${NC} $*"; exit 1; }

echo ""
echo -e "${GREEN}⚡ 充电站净利润风险仿真系统 — 一键启动${NC}"
echo "════════════════════════════════════════"

# ── 检查 Python ───────────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    err "未找到 Python，请先安装 Python 3.9+"
fi
PY_VER=$($PYTHON --version 2>&1)
log "使用 $PY_VER"

# ── 安装依赖 ──────────────────────────────────────────────────────────────────
log "正在安装/检查 Python 依赖…"
$PYTHON -m pip install -q -r "$BACKEND_DIR/requirements.txt" \
    && ok "依赖已就绪" \
    || err "依赖安装失败，请检查网络或手动运行: pip install -r backend/requirements.txt"

# ── 杀掉旧进程（如有）────────────────────────────────────────────────────────
kill_port() {
    local port=$1
    local pid
    pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        warn "端口 $port 已被占用（PID $pid），正在终止…"
        kill -9 "$pid" 2>/dev/null || true
        sleep 0.5
    fi
}
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT

# ── 启动后端 ──────────────────────────────────────────────────────────────────
log "启动 FastAPI 后端（端口 $BACKEND_PORT）…"
cd "$BACKEND_DIR"
$PYTHON -m uvicorn main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --log-level warning \
    > "$SCRIPT_DIR/.backend.log" 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# 等待后端就绪（最多 12 秒）
log "等待后端就绪…"
for i in $(seq 1 24); do
    if curl -sf "http://localhost:$BACKEND_PORT/" >/dev/null 2>&1; then
        ok "后端已启动 (PID $BACKEND_PID)  →  http://localhost:$BACKEND_PORT"
        break
    fi
    sleep 0.5
    if [ "$i" -eq 24 ]; then
        err "后端启动超时，查看日志：cat $SCRIPT_DIR/.backend.log"
    fi
done

# ── 启动前端静态服务 ──────────────────────────────────────────────────────────
log "启动前端静态服务（端口 $FRONTEND_PORT）…"
cd "$FRONTEND_DIR"
$PYTHON -m http.server $FRONTEND_PORT \
    > "$SCRIPT_DIR/.frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"
sleep 0.8
ok "前端已启动 (PID $FRONTEND_PID)  →  http://localhost:$FRONTEND_PORT"

# ── 自动打开浏览器 ────────────────────────────────────────────────────────────
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
log "正在打开浏览器…"
if command -v open &>/dev/null; then          # macOS
    open "$FRONTEND_URL"
elif command -v xdg-open &>/dev/null; then    # Linux
    xdg-open "$FRONTEND_URL" &
elif command -v start &>/dev/null; then       # Windows (Git Bash)
    start "$FRONTEND_URL"
else
    warn "无法自动打开浏览器，请手动访问：$FRONTEND_URL"
fi

# ── 摘要 ─────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}  🚀 系统已就绪！${NC}"
echo ""
echo -e "  前端展示：  ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "  后端 API：  ${BLUE}http://localhost:$BACKEND_PORT${NC}"
echo -e "  API 文档：  ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
echo ""
echo -e "  后端日志：  cat .backend.log"
echo -e "  前端日志：  cat .frontend.log"
echo ""
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo "════════════════════════════════════════"

# ── 捕获 Ctrl+C，优雅退出 ────────────────────────────────────────────────────
trap "echo ''; log '正在停止服务…'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; ok '已停止。'; exit 0" INT TERM

# 保持脚本运行，实时输出后端日志
tail -f "$SCRIPT_DIR/.backend.log" 2>/dev/null &
wait
