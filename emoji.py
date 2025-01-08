# 基础Emoji映射字典
EMOJI_MAPPINGS = {
    # 基础符号
    "notice": "ℹ️",
    "warning": "⚠️",
    "link": "🔗",
    "pin": "📌",
    "bookmark": "🔖",
    "star": "⭐",
    "sparkles": "✨",
    "fire": "🔥",
    "bell": "🔔",
    "speaker": "📢",
    "megaphone": "📣",
    
    # 金融相关
    "chart": "📊",
    "chart_up": "📈",
    "chart_down": "📉",
    "money": "💰",
    "dollar": "💵",
    "coin": "🪙",
    "credit_card": "💳",
    "bank": "🏦",
    "gem": "💎",
    "growth": "📈",
    "trending_up": "📈",
    "trending_down": "📉",
    "balance": "⚖️",
    
    # 时间相关
    "clock": "🕒",
    "calendar": "📅",
    "hourglass": "⌛",
    "timer": "⏲️",
    "alarm": "⏰",
    
    # 交互相关
    "click": "👆",
    "point_up": "☝️",
    "point_down": "👇",
    "point_right": "👉",
    "point_left": "👈",
    "check": "✅",
    "cross": "❌",
    "refresh": "🔄",
    "back": "⬅️",
    "forward": "➡️",
    
    # 状态相关
    "success": "✅",
    "fail": "❌",
    "pending": "⏳",
    "locked": "🔒",
    "unlocked": "🔓",
    "on": "🟢",
    "off": "🔴",
    "new": "🆕",
    "ok": "👌",
    "sos": "🆘",
    
    # 工具相关
    "tools": "🛠️",
    "wrench": "🔧",
    "hammer": "🔨",
    "gear": "⚙️",
    "key": "🔑",
    "lock": "🔒",
    "search": "🔍",
    "mag": "🔎",
    
    # 通讯相关
    "email": "📧",
    "inbox": "📥",
    "outbox": "📤",
    "envelope": "✉️",
    "phone": "📱",
    "computer": "💻",
    
    # 文档相关
    "file": "📄",
    "folder": "📁",
    "clipboard": "📋",
    "memo": "📝",
    "book": "📚",
    "page": "📃",
    "scroll": "📜",
    
    # 其他常用
    "rocket": "🚀",
    "target": "🎯",
    "bulb": "💡",
    "gift": "🎁",
    "package": "📦",
    "tag": "🏷️",
    "label": "🏷️",
    "shield": "🛡️",
    "crown": "👑",
    "trophy": "🏆",
    "medal": "🏅",
    "handshake": "🤝",
    "rainbow": "🌈",
    "cloud": "☁️",
    "zap": "⚡",
    "sparkle": "✨",
    "wave": "🌊",
    "globe": "🌐",
    
    # 特殊用途
    "crypto": "₿",
    "defi": "⛓️",
    "nft": "🎨",
    "mining": "⛏️",
    "wallet": "👛",
    "stake": "🥩",
    "airdrop": "🪂",
    "pool": "🌊",
    "swap": "🔄"
}

# Emoji和标题类型映射字典
ANNOUNCEMENT_MAPPINGS = {
    # 上币相关
    "Introducing": ("🚀", "新币上线公告"),
    "上线": ("🚀", "新币上线公告"),
    "Will List": ("🚀", "新币上线公告"),
    "New Fiat Listings": ("💵", "法币上线公告"),
    "New Spot Trading Pairs": ("💎", "现货交易对公告"),
    "New Trading Pairs": ("💎", "交易对公告"),
    "Seed Sale": ("🌱", "Seed Sale公告"),
    "Binance Launchpad": ("🚀", "Launchpad公告"),
    "Mystery Box": ("🎁", "盲盒公告"),
    "Innovation Zone": ("🔬", "创新区公告"),
    "创新区": ("🔬", "创新区公告"),
    "Delisting": ("⚠️", "下架公告"),
    "下架": ("⚠️", "下架公告"),
    
    # 交易相关
    "Launchpool": ("🌱", "Launchpool公告"),
    "Futures": ("📈", "合约公告"),
    "USDⓈ-M Futures": ("📈", "U本位合约公告"),
    "COIN-M Futures": ("📈", "币本位合约公告"),
    "期货": ("📈", "合约公告"),
    "Options": ("📊", "期权公告"),
    "期权": ("📊", "期权公告"),
    "Margin": ("💹", "杠杆公告"),
    "杠杆": ("💹", "杠杆公告"),
    "Spot": ("💎", "现货公告"),
    "现货": ("💎", "现货公告"),
    "Earn": ("💰", "赚币公告"),
    "Savings": ("💰", "活期理财公告"),
    "Staking": ("🏆", "质押公告"),
    "Dual Investment": ("💰", "双币理财公告"),
    "赚币": ("💰", "赚币公告"),
    "Liquid Swap": ("🌊", "流动性挖矿公告"),
    "流动性": ("🌊", "流动性挖矿公告"),
    "Convert": ("🔄", "快捷兑换公告"),
    "兑换": ("🔄", "快捷兑换公告"),
    "P2P": ("👥", "场外交易公告"),
    "Fan Token": ("🎭", "粉丝币公告"),
    "粉丝币": ("🎭", "粉丝币公告"),
    "ETF": ("📊", "ETF公告"),
    
    # 系统相关
    "Maintenance": ("🔧", "系统维护公告"),
    "System Upgrade": ("🔧", "系统升级公告"),
    "System Update": ("🔧", "系统更新公告"),
    "维护": ("🔧", "系统维护公告"),
    "Update": ("🔄", "系统更新公告"),
    "更新": ("🔄", "系统更新公告"),
    "API": ("🔌", "API公告"),
    "Security": ("🔒", "安全公告"),
    "安全": ("🔒", "安全公告"),
    "Risk Warning": ("⚠️", "风险提示"),
    "风险提示": ("⚠️", "风险提示"),
    
    # 活动相关
    "Rewards": ("🎁", "奖励公告"),
    "奖励": ("🎁", "奖励公告"),
    "Campaign": ("🎯", "活动公告"),
    "活动": ("🎯", "活动公告"),
    "Airdrop": ("🪂", "空投公告"),
    "空投": ("🪂", "空投公告"),
    "Staking": ("🏆", "质押公告"),
    "质押": ("🏆", "质押公告"),
    "Trading Competition": ("🏅", "交易大赛公告"),
    "交易大赛": ("🏅", "交易大赛公告"),
    "Learn and Earn": ("📚", "学习赚币公告"),
    "学习赚币": ("📚", "学习赚币公告"),
    "NFT": ("🎨", "NFT公告"),
    "Promotion": ("🎉", "促销活动公告"),
    "促销": ("🎉", "促销活动公告"),
    "VIP": ("👑", "VIP公告"),
    "Referral": ("🤝", "推荐计划公告"),
    "推荐": ("🤝", "推荐计划公告"),
    "Bonus": ("🎁", "福利公告"),
    "福利": ("🎁", "福利公告"),
    
    # 其他重要类型
    "Wallet": ("👛", "钱包公告"),
    "钱包": ("👛", "钱包公告"),
    "Fiat": ("💵", "法币公告"),
    "法币": ("💵", "法币公告"),
    "DeFi": ("⛓️", "DeFi公告"),
    "Card": ("💳", "卡公告"),
    "信用卡": ("💳", "卡公告"),
    "Binance Pay": ("💳", "支付公告"),
    "支付": ("💳", "支付公告"),
    "Crypto Loans": ("💰", "借贷公告"),
    "借贷": ("💰", "借贷公告"),
    "Gift Card": ("🎁", "礼品卡公告"),
    "礼品卡": ("🎁", "礼品卡公告"),
    
    # 通用类型
    "Announcement": ("📣", "公告"),
    "公告": ("📣", "公告"),
    "Notice": ("ℹ️", "通知公告"),
    "通知": ("ℹ️", "通知公告")
}

def get_emoji_and_type(title: str) -> tuple:
    """根据标题返回相应的emoji和公告类型
    
    Args:
        title: 公告标题
        
    Returns:
        tuple: (emoji, announcement_type)
    """
    for keyword, (emoji, announcement_type) in ANNOUNCEMENT_MAPPINGS.items():
        if keyword in title:
            return emoji, announcement_type
    return "ℹ️", "公告"