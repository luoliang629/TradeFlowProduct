# 数据库 Docker 部署

## 数据库连接信息

本环境包含四个数据库：MySQL 8、PostgreSQL 16、Redis 7 和 MinIO

## MySQL 8

### 基本信息
- **数据库类型**: MySQL 8.4.6
- **容器名称**: mysql8
- **端口映射**: 3306:3306
- **数据存储**: ./mysql_data
- **自动启动**: 已启用 (--restart=always)

### 连接参数
- **主机地址**: 127.0.0.1 或 localhost
- **端口**: 3306
- **用户名**: root
- **密码**: root
- **访问权限**: 支持本地和远程连接

### 连接方式

#### 1. 容器内连接
```bash
docker exec -it mysql8 mysql -u root -proot
```

#### 2. 本地客户端连接
```bash
# 使用 127.0.0.1
mysql -h 127.0.0.1 -P 3306 -u root -proot

# 使用 localhost
mysql -h localhost -P 3306 -u root -proot
```

#### 3. 应用程序连接字符串
```
# JDBC URL
jdbc:mysql://127.0.0.1:3306/database_name?useSSL=false&serverTimezone=UTC

# Node.js (mysql2)
mysql://root:root@127.0.0.1:3306/database_name

# Python (PyMySQL)
mysql+pymysql://root:root@127.0.0.1:3306/database_name
```

### 容器管理命令

#### 启动/停止容器
```bash
# 启动容器
docker start mysql8

# 停止容器
docker stop mysql8

# 重启容器
docker restart mysql8

# 查看容器状态
docker ps -a | grep mysql8

# 查看容器日志
docker logs mysql8
```

#### 数据备份与恢复
```bash
# 备份数据库
docker exec mysql8 mysqldump -u root -proot database_name > backup.sql

# 恢复数据库
docker exec -i mysql8 mysql -u root -proot database_name < backup.sql
```

### 安全警告
⚠️ **当前配置仅适用于开发环境**
- 使用弱密码 (root/root)
- 允许远程连接
- 生产环境请修改安全配置

### 目录结构
```
dbdata/
├── README.md          # 本文档
├── mysql_data/        # MySQL数据目录
│   ├── mysql/         # 系统数据库
│   ├── performance_schema/
│   ├── sys/
│   └── ...           # 其他MySQL文件
├── postgres_data/     # PostgreSQL数据目录
│   ├── base/          # 数据库文件
│   ├── pg_wal/        # WAL日志
│   ├── global/        # 全局数据
│   └── ...           # 其他PostgreSQL文件
└── redis_data/        # Redis数据目录
    └── appendonlydir/ # AOF持久化文件
        ├── appendonly.aof.manifest
        └── ...       # 其他Redis文件
```

## 快速操作指南

### 同时管理三个数据库
```bash
# 查看所有数据库容器
docker ps | grep -E "(mysql8|postgres16|redis7)"

# 同时停止三个数据库
docker stop mysql8 postgres16 redis7

# 同时启动三个数据库
docker start mysql8 postgres16 redis7

# 同时重启三个数据库
docker restart mysql8 postgres16 redis7
```

### 资源监控
```bash
# 查看容器资源使用
docker stats mysql8 postgres16 redis7

# 查看容器详细信息
docker inspect mysql8
docker inspect postgres16
docker inspect redis7

# 检查端口占用
lsof -i :3306  # MySQL
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

---
## PostgreSQL 16

### 基本信息
- **数据库类型**: PostgreSQL 16.x
- **容器名称**: postgres16
- **端口映射**: 5432:5432
- **数据存储**: ./postgres_data
- **自动启动**: 已启用 (--restart=always)

### 连接参数
- **主机地址**: 127.0.0.1 或 localhost
- **端口**: 5432
- **用户名**: postgres
- **密码**: root
- **默认数据库**: mydb

### 连接方式

#### 1. 容器内连接
```bash
docker exec -it postgres16 psql -U postgres -d mydb
```

#### 2. 本地客户端连接
```bash
# 使用 psql 客户端
psql -h 127.0.0.1 -p 5432 -U postgres -d mydb

# 或使用完整连接字符串
psql "postgresql://postgres:root@127.0.0.1:5432/mydb"
```

#### 3. 应用程序连接字符串
```
# JDBC URL
jdbc:postgresql://127.0.0.1:5432/mydb?user=postgres&password=root

# Node.js (pg)
postgresql://postgres:root@127.0.0.1:5432/mydb

# Python (psycopg2)
postgresql://postgres:root@127.0.0.1:5432/mydb

# Django settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

### 容器管理命令

#### 启动/停止容器
```bash
# 启动容器
docker start postgres16

# 停止容器
docker stop postgres16

# 重启容器
docker restart postgres16

# 查看容器状态
docker ps -a | grep postgres16

# 查看容器日志
docker logs postgres16
```

#### 数据备份与恢复
```bash
# 备份数据库
docker exec postgres16 pg_dump -U postgres mydb > backup.sql

# 恢复数据库
docker exec -i postgres16 psql -U postgres -d mydb < backup.sql

# 备份所有数据库
docker exec postgres16 pg_dumpall -U postgres > full_backup.sql
```

---
## Redis 7

### 基本信息
- **数据库类型**: Redis 7.x (内存数据库)
- **容器名称**: redis7
- **端口映射**: 6379:6379
- **数据存储**: ./redis_data
- **自动启动**: 已启用 (--restart=always)

### 连接参数
- **主机地址**: 127.0.0.1 或 localhost
- **端口**: 6379
- **密码**: root
- **持久化**: 启用 RDB + AOF 双重持久化

### 连接方式

#### 1. 容器内连接
```bash
docker exec -it redis7 redis-cli -a root
```

#### 2. 本地客户端连接
```bash
# 使用 redis-cli 客户端
redis-cli -h 127.0.0.1 -p 6379 -a root

# 或使用连接字符串
redis-cli -u redis://:root@127.0.0.1:6379
```

#### 3. 应用程序连接字符串
```
# Node.js (redis)
redis://root@127.0.0.1:6379

# Python (redis-py)
redis://root@127.0.0.1:6379

# Java (Jedis)
redis://root@127.0.0.1:6379

# Go (go-redis)
redis://root@127.0.0.1:6379

# PHP (predis)
redis://root@127.0.0.1:6379
```

### 容器管理命令

#### 启动/停止容器
```bash
# 启动容器
docker start redis7

# 停止容器
docker stop redis7

# 重启容器
docker restart redis7

# 查看容器状态
docker ps -a | grep redis7

# 查看容器日志
docker logs redis7
```

#### 数据备份与恢复
```bash
# 手动触发 RDB 快照
docker exec redis7 redis-cli -a root BGSAVE

# 查看持久化状态
docker exec redis7 redis-cli -a root LASTSAVE

# 备份数据文件（需要先停止容器）
docker stop redis7
cp redis_data/appendonlydir/* /backup/location/
docker start redis7

# 查看内存使用情况
docker exec redis7 redis-cli -a root INFO memory
```

#### 常用 Redis 命令
```bash
# 基本操作
docker exec redis7 redis-cli -a root SET key value
docker exec redis7 redis-cli -a root GET key
docker exec redis7 redis-cli -a root DEL key

# 查看所有键
docker exec redis7 redis-cli -a root KEYS "*"

# 查看数据库信息
docker exec redis7 redis-cli -a root INFO

# 清空当前数据库（谨慎使用）
docker exec redis7 redis-cli -a root FLUSHDB

# 监控 Redis 命令
docker exec redis7 redis-cli -a root MONITOR
```

---
## MinIO

### 基本信息
- **对象存储**: MinIO (S3兼容的对象存储)
- **容器名称**: minio
- **端口映射**: 9000:9000 (API), 9001:9001 (Console)
- **数据存储**: ./minio_data
- **自动启动**: 已启用 (--restart=always)

### 连接参数
- **API地址**: http://127.0.0.1:9000
- **Console地址**: http://127.0.0.1:9001
- **用户名**: root
- **密码**: rootpassword

### 连接方式

#### 1. 控制台访问
通过浏览器访问管理控制台：
```
http://127.0.0.1:9001
```

#### 2. 应用程序连接字符串
```
# AWS SDK (JavaScript)
const s3 = new AWS.S3({
  endpoint: 'http://127.0.0.1:9000',
  accessKeyId: 'root',
  secretAccessKey: 'rootpassword',
  s3ForcePathStyle: true
});

# Python (boto3)
import boto3
s3 = boto3.client('s3',
  endpoint_url='http://127.0.0.1:9000',
  aws_access_key_id='root',
  aws_secret_access_key='rootpassword'
)

# Java (AWS SDK)
AmazonS3 s3 = AmazonS3ClientBuilder.standard()
  .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration("http://127.0.0.1:9000", "us-east-1"))
  .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials("root", "rootpassword")))
  .withPathStyleAccessEnabled(true)
  .build();

# mc客户端
mc alias set local http://127.0.0.1:9000 root rootpassword
```

### 容器管理命令

#### 启动/停止容器
```bash
# 启动容器
docker start minio

# 停止容器
docker stop minio

# 重启容器
docker restart minio

# 查看容器状态
docker ps -a | grep minio

# 查看容器日志
docker logs minio
```

#### 数据管理命令
```bash
# 使用mc客户端管理
mc ls local/
mc mb local/mybucket
mc cp file.txt local/mybucket/
mc ls local/mybucket/

# 查看存储信息
mc admin info local/

# 监控存储状态
mc admin monitor local/
```

#### 常用MinIO命令
```bash
# 创建bucket
docker exec minio mc mb local/mybucket

# 上传文件
docker exec minio mc cp /path/to/file local/mybucket/

# 下载文件
docker exec minio mc cp local/mybucket/file.txt /path/to/destination/

# 列出文件
docker exec minio mc ls local/mybucket/

# 删除文件
docker exec minio mc rm local/mybucket/file.txt

# 删除bucket
docker exec minio mc rb local/mybucket
```

### 安全警告
⚠️ **当前配置仅适用于开发环境**
- 使用简单密码 (root/rootpassword)
- 没有启用TLS加密
- 生产环境请修改安全配置

### 目录结构
```
dbdata/
├── README.md          # 本文档
├── mysql_data/        # MySQL数据目录
├── postgres_data/     # PostgreSQL数据目录
├── redis_data/        # Redis数据目录
└── minio_data/        # MinIO数据目录
    ├── .minio.sys/    # MinIO系统文件
    └── ...           # 其他MinIO文件
```

## 快速操作指南

### 同时管理四个数据库
```bash
# 查看所有数据库容器
docker ps | grep -E "(mysql8|postgres16|redis7|minio)"

# 同时停止四个数据库
docker stop mysql8 postgres16 redis7 minio

# 同时启动四个数据库
docker start mysql8 postgres16 redis7 minio

# 同时重启四个数据库
docker restart mysql8 postgres16 redis7 minio
```

### 资源监控
```bash
# 查看容器资源使用
docker stats mysql8 postgres16 redis7 minio

# 查看容器详细信息
docker inspect mysql8
docker inspect postgres16
docker inspect redis7
docker inspect minio

# 检查端口占用
lsof -i :3306  # MySQL
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :9000  # MinIO API
lsof -i :9001  # MinIO Console
```

---
*创建时间: $(date)*
*MySQL版本: 8.4.6 | PostgreSQL版本: 16.x | Redis版本: 7.x | MinIO版本: RELEASE.2025-07-23T15-54-02Z*
*Docker镜像: mysql:8, postgres:16, redis:7-alpine, quay.io/minio/minio*