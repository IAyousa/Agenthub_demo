"""
AgentHub Agent Service — 应用入口

本文件是 FastAPI 应用的主入口，负责：
  - 创建 FastAPI 应用实例
  - 配置 CORS 中间件
  - 注册路由
  - 定义全局异常处理（统一错误格式，对齐 API 契约文档第 5 节）
  - 提供根路径和健康检查端点

启动方式：
    uvicorn main:app --port 8000

Swagger 文档：
    启动后访问 http://localhost:8000/docs
"""

import sys
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import messages
from config import settings
from models import ErrorResponse, HealthResponse

START_TIME = time.time()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="""
AgentHub Agent 服务是 Multi-Agent Collaboration Platform 的 AI 推理层，
通过统一的 REST API 接口，将上游（Java 后端）转发的用户消息分发给配置的
AI Agent（Claude Code CLI、Codex CLI）并流式返回生成结果。

## 核心能力
- **多 Agent 支持**：Claude Code CLI / Codex CLI
- **流式响应**：SSE 协议逐 token 推送
- **本地执行**：CLI Agent 可在本机读写文件、执行 shell 命令
- **统一错误格式**：所有错误遵循 `{error, message, timestamp, path}` 结构

## 接口分类
| 端点 | 说明 |
|------|------|
| `GET /` | 服务欢迎页 |
| `GET /health` | 健康检查 |
| `POST /api/agent/chat` | Agent 对话（流式/非流式） |

## 相关文档
- API 契约定义：`docs/API 契约定义与通信协议规范.md` 第 4 节
- 基础设施配置：`docs/基础设施配置.md`
""",
    openapi_tags=[
        {
            "name": "agent",
            "description": "Agent 调用接口，接收 Java 后端转发的对话请求并返回 AI 生成内容。",
        },
        {
            "name": "health",
            "description": "服务健康检查接口。",
        },
    ],
    contact={
        "name": "AgentHub Team",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router, prefix="/api/agent", tags=["agent"])


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = _original_openapi()

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            responses = operation.get("responses", {})
            if "422" in responses:
                del responses["422"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


_original_openapi = app.openapi
app.openapi = _custom_openapi


def _error_response(status_code: int, error_code: str, message: str, path: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error_code,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            path=path,
        ).model_dump(),
    )


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Exception):
    return _error_response(400, "VALIDATION_ERROR", str(exc), request.url.path)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = errors[0].get("msg", "请求参数校验失败") if errors else "请求参数校验失败"
    return _error_response(400, "VALIDATION_ERROR", message, request.url.path)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return _error_response(404, "NOT_FOUND", str(exc), request.url.path)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return _error_response(500, "INTERNAL_ERROR", str(exc), request.url.path)


@app.get(
    "/",
    summary="服务欢迎页",
    description="返回服务基本信息和文档入口链接。",
    tags=["health"],
    response_model=dict,
    responses={
        200: {
            "description": "服务正常",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to Agenthub API",
                        "docs": "/docs",
                    }
                }
            },
        },
    },
)
async def root():
    return {"message": "Welcome to Agenthub API", "docs": "/docs"}


@app.get(
    "/health",
    summary="健康检查",
    description="""
返回 Agent 服务的运行状态、版本号和已运行时间。

对齐 API 契约文档第 4.3 节：
- `status`: 正常时返回 "ok"
- `version`: 服务版本号
- `uptime`: 从启动到当前的运行秒数
""",
    tags=["health"],
    response_model=HealthResponse,
    responses={
        200: {
            "description": "服务健康",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "version": "1.0.0",
                        "uptime": 3600,
                    }
                }
            },
        },
    },
)
async def health():
    uptime_seconds = int(time.time() - START_TIME)
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        uptime=uptime_seconds,
    )
