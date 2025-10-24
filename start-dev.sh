#!/bin/bash

# AI TravelTailor Development Environment Startup Script
# 백엔드와 프론트엔드를 동시에 실행합니다

set -e

echo "🚀 AI TravelTailor 개발 환경을 시작합니다..."
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 환경 변수 파일 확인
check_env_files() {
    echo -e "${BLUE}📋 환경 변수 파일 확인 중...${NC}"

    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}❌ backend/.env 파일이 없습니다${NC}"
        echo -e "${YELLOW}   다음 명령어로 생성해주세요: cp backend/.env.example backend/.env${NC}"
        exit 1
    fi

    if [ ! -f "frontend/.env.local" ]; then
        echo -e "${YELLOW}⚠️  frontend/.env.local 파일이 없습니다${NC}"
        echo -e "${YELLOW}   다음 명령어로 생성해주세요: cp frontend/.env.example frontend/.env.local${NC}"
        echo -e "${YELLOW}   기본값으로 진행합니다...${NC}"
    fi

    echo -e "${GREEN}✅ 환경 변수 확인 완료${NC}"
    echo ""
}

# 의존성 확인
check_dependencies() {
    echo -e "${BLUE}🔍 필수 도구 확인 중...${NC}"

    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3이 설치되어 있지 않습니다${NC}"
        exit 1
    fi

    # uv 확인
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv가 설치되어 있지 않습니다${NC}"
        echo -e "${YELLOW}   설치: pip install uv${NC}"
        exit 1
    fi

    # Node.js 확인
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다${NC}"
        exit 1
    fi

    # pnpm 확인
    if ! command -v pnpm &> /dev/null; then
        echo -e "${RED}❌ pnpm이 설치되어 있지 않습니다${NC}"
        echo -e "${YELLOW}   설치: npm install -g pnpm${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ 필수 도구 확인 완료${NC}"
    echo ""
}

# 백엔드 의존성 설치
setup_backend() {
    echo -e "${BLUE}📦 백엔드 의존성 설치 중...${NC}"
    cd backend

    # 가상환경이 없으면 생성
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}   가상환경 생성 중...${NC}"
        uv venv
    fi

    # 의존성 설치
    source .venv/bin/activate
    uv pip install -e ".[dev]" --quiet

    echo -e "${GREEN}✅ 백엔드 의존성 설치 완료${NC}"
    cd ..
    echo ""
}

# 프론트엔드 의존성 설치
setup_frontend() {
    echo -e "${BLUE}🎨 프론트엔드 의존성 설치 중...${NC}"
    cd frontend

    # node_modules가 없으면 설치
    if [ ! -d "node_modules" ]; then
        pnpm install --silent
    fi

    echo -e "${GREEN}✅ 프론트엔드 의존성 설치 완료${NC}"
    cd ..
    echo ""
}

# 데이터베이스 마이그레이션
run_migrations() {
    echo -e "${BLUE}🗄️  데이터베이스 마이그레이션 실행 중...${NC}"
    cd backend
    source .venv/bin/activate

    # 마이그레이션 실행
    if uv run alembic upgrade head 2>/dev/null; then
        echo -e "${GREEN}✅ 마이그레이션 완료${NC}"
    else
        echo -e "${YELLOW}⚠️  마이그레이션 실패 (데이터베이스 연결 확인 필요)${NC}"
    fi

    cd ..
    echo ""
}

# 서비스 시작
start_services() {
    echo -e "${BLUE}🚀 서비스 시작 중...${NC}"
    echo ""

    # 백엔드 시작
    echo -e "${GREEN}📦 백엔드 서버 시작...${NC}"
    cd backend
    source .venv/bin/activate
    uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # 잠시 대기 (백엔드가 먼저 시작되도록)
    sleep 2

    # 프론트엔드 시작
    echo -e "${GREEN}🎨 프론트엔드 서버 시작...${NC}"
    cd frontend
    pnpm dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # 잠시 대기 (서버 시작 대기)
    sleep 3

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✨ 모든 서비스가 시작되었습니다!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}🌐 접속 URL:${NC}"
    echo -e "   ${YELLOW}프론트엔드:${NC} http://localhost:3000"
    echo -e "   ${YELLOW}백엔드 API:${NC} http://localhost:8000/docs"
    echo -e "   ${YELLOW}Health Check:${NC} http://localhost:8000/health"
    echo ""
    echo -e "${BLUE}📝 로그 파일:${NC}"
    echo -e "   ${YELLOW}백엔드:${NC} tail -f logs/backend.log"
    echo -e "   ${YELLOW}프론트엔드:${NC} tail -f logs/frontend.log"
    echo ""
    echo -e "${RED}🛑 종료하려면 Ctrl+C를 누르세요${NC}"
    echo ""

    # 종료 시 프로세스 정리
    trap "cleanup" EXIT INT TERM

    # 대기
    wait
}

# 정리 함수
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 서비스를 종료합니다...${NC}"

    # 백엔드 종료
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ 백엔드 서버 종료${NC}"
    fi

    # 프론트엔드 종료
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ 프론트엔드 서버 종료${NC}"
    fi

    # 포트 정리 (혹시 남아있는 프로세스)
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}👋 종료되었습니다${NC}"
    exit 0
}

# 로그 디렉토리 생성
mkdir -p logs

# 메인 실행 흐름
main() {
    check_env_files
    check_dependencies

    # --skip-install 옵션이 없으면 의존성 설치
    if [ "$1" != "--skip-install" ]; then
        setup_backend
        setup_frontend
        run_migrations
    else
        echo -e "${YELLOW}⏭️  의존성 설치 건너뛰기 (--skip-install)${NC}"
        echo ""
    fi

    start_services
}

# 도움말
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "AI TravelTailor 개발 환경 실행 스크립트"
    echo ""
    echo "사용법:"
    echo "  ./start-dev.sh              # 모든 설정 후 서비스 시작"
    echo "  ./start-dev.sh --skip-install   # 의존성 설치 건너뛰고 바로 시작"
    echo "  ./start-dev.sh --help       # 도움말 표시"
    echo ""
    exit 0
fi

main "$@"
