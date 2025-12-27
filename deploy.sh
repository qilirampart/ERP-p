#!/bin/bash

# 印刷ERP系统 - 快速部署脚本

set -e

echo "========================================="
echo "  印刷ERP系统 - Docker快速部署"
echo "========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "   安装指南：https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker和Docker Compose已安装"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    cp .env.example .env

    # 生成随机密码
    MYSQL_ROOT_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    MYSQL_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    SECRET_KEY=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-48)

    # 替换占位符
    sed -i "s/your_secure_root_password_here/$MYSQL_ROOT_PWD/" .env
    sed -i "s/your_secure_password_here/$MYSQL_PWD/" .env
    sed -i "s/your_very_secure_secret_key_at_least_32_characters_long/$SECRET_KEY/" .env

    echo "✅ .env文件已创建并配置随机密码"
    echo ""
else
    echo "✅ .env文件已存在"
    echo ""
fi

# 询问是否重新构建
echo "选择部署方式："
echo "  1) 快速启动（使用现有镜像）"
echo "  2) 完整构建（重新构建所有镜像）"
read -p "请选择 [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 正在启动服务..."
        docker compose up -d
        ;;
    2)
        echo ""
        echo "🔨 正在构建镜像..."
        docker compose build --no-cache
        echo ""
        echo "🚀 正在启动服务..."
        docker compose up -d
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker compose ps

echo ""
echo "========================================="
echo "  ✅ 部署完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  前端界面: http://localhost"
echo "  后端API:  http://localhost:8000"
echo "  API文档:  http://localhost:8000/docs"
echo ""
echo "默认管理员账号："
echo "  用户名: admin"
echo "  密码:   admin123"
echo ""
echo "⚠️  首次登录后请立即修改密码！"
echo ""
echo "常用命令："
echo "  查看日志:  docker compose logs -f"
echo "  停止服务:  docker compose down"
echo "  重启服务:  docker compose restart"
echo ""
