def character_stat_translator(character_stat_name):
    character_stat_name_dict = {
        "hp": "基础生命值",
        "atk": "基础攻击力",
        "def": "基础防御力",
        "critrate": "暴击率",
        "critdmg": "暴击伤害",
        "bonuscritdmg": "暴击伤害",
        "bonuscritrate": "暴击率",
        "bonushp": "生命值",
        "bonusatk": "攻击力",
        "bonusdef": "防御力",
        "bonusheal": "治疗加成",
        "bonusem": "元素精通",
        "bonuser": "元素充能效率",
        "bonusphys":"物理伤害",
        "bonusanemo": "风元素伤害",
        "bonusgeo": "岩元素伤害",
        "bonushydro": "水元素伤害",
        "bonuselec": "雷元素伤害",
        "bonuscryo": "冰元素伤害",
        "bonuspyro": "火元素伤害",
        "bonusdendro": "草元素伤害"
    }
    try:
        return character_stat_name_dict[character_stat_name.lower().strip().replace("%", "")]
    except KeyError:
        return character_stat_name
