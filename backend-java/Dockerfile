# AgentHub Backend — Multi-stage Docker Build
# Stage 1: Maven build
# Stage 2: JRE runtime

# ============================================
# Stage 1: Build
# ============================================
FROM maven:3.9-eclipse-temurin-17-alpine AS builder

WORKDIR /build
COPY pom.xml .
# 先下载依赖（利用 Docker 缓存层）
RUN mvn dependency:go-offline -q

COPY src ./src
RUN mvn package -DskipTests -q

# ============================================
# Stage 2: Run
# ============================================
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# 创建数据目录
RUN mkdir -p /data/h2 /data/artifacts /data/workspaces

# 复制 JAR
COPY --from=builder /build/target/*.jar app.jar

# 环境变量（docker-compose 或 docker run 时覆盖）
ENV JWT_SECRET=change-me-in-production
ENV AGENT_SERVICE_URL=http://agent:8000
ENV CORS_ORIGINS=http://localhost
ENV SPRING_PROFILES_ACTIVE=

EXPOSE 8080

# 使用环境变量覆盖 Spring 配置
ENTRYPOINT ["sh", "-c", "java \
  -Dserver.port=8080 \
  -Dagent.service.url=${AGENT_SERVICE_URL} \
  -Dagent.workspace.root=/data/workspaces \
  -Dartifact.storage.path=/data/artifacts \
  -Dcors.allowed-origins=${CORS_ORIGINS} \
  -Djwt.secret=${JWT_SECRET} \
  -Dspring.datasource.url=jdbc:h2:file:/data/h2/agenthub\;AUTO_SERVER=TRUE \
  ${JAVA_OPTS} \
  -jar app.jar"]
