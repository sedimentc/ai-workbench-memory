---
id: IMPORT-008
type: imported_material
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: 导入资料
sensitivity: internal
last_reviewed: 2026-05-20
source: /Users/sediment/Documents/btc-etf-dashboard/README.md
---

# btc-etf-dashboard README

## 来源

```text
/Users/sediment/Documents/btc-etf-dashboard/README.md
```

## 原文

# BTC-ETF 实时看板

> 比特币 + ETF资金流入流出 + 美股联动 实时监控看板

## 功能特性

- **🪙 BTC价格趋势** - 实时价格与24h涨跌幅
- **📈 ETF净流入流出** - 美国比特币ETF每日资金动向
- **📉 美股走势** - 纳指/标普涨跌情况
- **⚠️ 风险状态卡** - 综合风险评估与预警

## 快速开始

### 1. 安装依赖

```bash
cd /Users/sediment/Documents/btc-etf-dashboard
npm install
```

### 2. 启动服务

```bash
./start.sh
```

### 3. 访问看板

浏览器打开: **http://localhost:3100**

## API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/metrics` | GET | 获取历史数据 (默认30条) |
| `/api/stream` | GET | SSE实时数据推送 |
| `/api/health` | GET | 服务健康检查 |
| `/api/refresh` | POST | 手动刷新数据 |

### 数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `date_et` | TEXT | 日期(美东时区) |
| `btc_price` | REAL | BTC价格(USD) |
| `btc_ret_1d` | REAL | BTC 24h涨跌幅(%) |
| `etf_net_flow_usd` | REAL | ETF净流入(百万美元) |
| `ndx_ret_1d` | REAL | 纳指涨跌幅(%) |
| `spx_ret_1d` | REAL | 标普涨跌幅(%) |
| `dxy` | REAL | 美元指数 |
| `vix` | REAL | 恐惧贪婪指数 |
| `stale` | INTEGER | 数据是否过期(0/1) |
| `source_url` | TEXT | 数据来源URL |
| `fetched_at` | TEXT | 数据获取时间(ISO) |

## 管理命令

```bash
# 启动
./start.sh

# 停止
./stop.sh

# 重启
./restart.sh

# 手动获取数据
node scripts/fetch-data.js
```

## 定时任务

使用OpenClaw设置每日美东收盘后自动更新：

```bash
openclaw cron add \
  --name "BTC-ETF Daily Update" \
  --cron "0 17 * * 1-5" \
  --tz "America/New_York" \
  --message "cd /Users/sediment/Documents/btc-etf-dashboard && node scripts/fetch-data.js"
```

## 数据来源

- **BTC价格**: CoinGecko API (免费)
- **美股指数**: Yahoo Finance (免费)
- **ETF数据**: Farside.co.uk (爬虫/估算)
- **恐惧贪婪指数**: Alternative.me (免费)

## 自动刷新

- 每60秒自动刷新数据
- SSE实时推送更新
- 支持手动刷新按钮

## 故障排除

### 端口被占用

```bash
# 查看3100端口
lsof -i:3100

# 强制停止
./stop.sh
```

### 依赖安装失败

```bash
# 清除缓存重装
rm -rf node_modules package-lock.json
npm install
```

### 数据获取失败

检查网络连接，部分API有频率限制：
- CoinGecko: 免费API限制 10-50次/分钟
- Yahoo Finance: 偶尔不稳定，已内置重试

### SQLite错误

```bash
# 重建数据库
rm data/metrics.db
./start.sh
```

## 项目结构

```
btc-etf-dashboard/
├── backend/
│   └── server.js        # Express服务器
├── frontend/
│   ├── index.html       # 前端页面
│   ├── style.css        # 样式
│   └── app.js           # 前端逻辑
├── scripts/
│   └── fetch-data.js    # 数据抓取
├── data/
│   └── metrics.db       # SQLite数据库
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
├── restart.sh           # 重启脚本
├── package.json         # 项目配置
└── README.md            # 说明文档
```

## 技术栈

- **后端**: Node.js + Express + better-sqlite3
- **前端**: 原生HTML/CSS/JavaScript
- **数据**: CoinGecko, Yahoo Finance, Alternative.me

## 风险状态说明

| 状态 | 条件 | 建议 |
|------|------|------|
| 🟢 低风险 | ETF大额流入 + BTC上涨 | 关注买入机会 |
| 🟡 注意 | 美股跌BTC未跌 | 刘大策略：先跑 |
| 🔴 高风险 | ETF大额流出 + BTC下跌 | 离场观望 |

---

**创建时间**: 2026-03-05  
**维护者**: sediment
