import time
import re
import json
from getCity import getCharacterCity, getTalentCity, getWeeklyItemName
from translator import character_stat_translator

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def de_optimized_image_url(image_url: str) -> str:
    if image_url.endswith(".webp"):
        image_url = image_url.replace(".webp", ".png")
    re_result = re.search(r"(\w|\d)+(\_)(\d)+(_\d\d)(.png$)", image_url)
    if re_result is None:
        return image_url
    else:
        return image_url[:-7] + ".png"


def GetChrome() -> webdriver.Chrome:
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    with open("./puppeteer-extra/stealth.min.js") as f:
        js = f.read()
    d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js
    })
    return d


def fetch_character_data(url: str) -> dict:
    character_special_talent_name = ""
    character_page_driver = GetChrome()
    character_page_driver.get(url)
    time.sleep(3)
    this_character_key_name = re.search(r"(\w)+(_(\d){3})", url).group().split("_")[0]
    # Capture character name from title
    character_name = character_page_driver.find_element(By.CLASS_NAME, "wp-block-post-title").text
    print("character name: " + character_name)
    # Find character stat table area
    character_table = character_page_driver.find_element(By.CSS_SELECTOR, "table.genshin_table.main_table")
    character_table_rows = character_table.find_elements(By.TAG_NAME, "tr")
    # Transverse each row in the table
    for row in character_table_rows:
        columns_at_this_row = row.find_elements(By.TAG_NAME, "td")
        if columns_at_this_row[0].text == "Title":
            character_title = columns_at_this_row[1].text
        elif columns_at_this_row[0].text == "Rarity":
            character_rarity = len(columns_at_this_row[1].find_elements(By.CLASS_NAME, "cur_icon"))
        elif columns_at_this_row[0].text == "Element":
            character_element_url = columns_at_this_row[1].find_element(By.TAG_NAME, "img").get_attribute("src")
        elif "Constellation" in columns_at_this_row[0].text:
            character_constellation = columns_at_this_row[1].text
        elif columns_at_this_row[0].text == "Description":
            character_description = columns_at_this_row[1].text
        elif columns_at_this_row[0].text == "Skill Ascension Materials":
            character_talent_materials = columns_at_this_row[1].find_elements(By.TAG_NAME, "a")
            if len(character_talent_materials) == 5:
                # Talent
                character_talent = character_talent_materials[2].find_element(By.TAG_NAME, "img")
                character_talent_materials_name = character_talent.get_attribute("alt")[1:3]
                character_talent_materials_img_url = character_talent.get_attribute("src")
                # Weekly
                character_weekly = character_talent_materials[3].find_element(By.TAG_NAME, "img")
                character_weekly_materials_name = character_weekly.get_attribute("alt")
                character_weekly_materials_img_url = character_weekly.get_attribute("src")
        elif columns_at_this_row[0].text == "Character Ascension Materials":
            character_ascension_materials = columns_at_this_row[1].find_elements(By.TAG_NAME, "a")
            if len(character_ascension_materials) == 9:
                # GemStone
                character_gemstone = character_ascension_materials[3].find_element(By.TAG_NAME, "img")
                character_gemstone_materials_name = character_gemstone.get_attribute("alt")
                character_gemstone_materials_img_url = character_gemstone.get_attribute("src")
                # Boss
                character_boss = character_ascension_materials[4].find_element(By.TAG_NAME, "img")
                character_boss_materials_name = character_boss.get_attribute("alt")
                character_boss_materials_img_url = character_boss.get_attribute("src")
                # Local
                character_local = character_ascension_materials[5].find_element(By.TAG_NAME, "img")
                character_local_materials_name = character_local.get_attribute("alt")
                character_local_materials_img_url = character_local.get_attribute("src")
                # Monster
                character_monster = character_ascension_materials[6].find_element(By.TAG_NAME, "img")
                character_monster_materials_name = character_monster.get_attribute("alt")
                character_monster_materials_img_url = character_monster.get_attribute("src")
    # Entire data table area
    entire_table_area = character_page_driver.find_element(By.CSS_SELECTOR, "div.tab-panels.tab-panels-1")
    # Character Stat Table
    character_stat_table = entire_table_area.find_element(By.ID, "char_stats") \
        .find_element(By.CSS_SELECTOR, "table.genshin_table.stat_table")
    character_stat_table_list = []
    # Character Stat Table Title
    character_stat_table_title_element = character_stat_table.find_element(By.TAG_NAME, "thead") \
        .find_elements(By.TAG_NAME, "td")
    character_stat_table_title = list([x.text for x in character_stat_table_title_element if "Materials" not in x.text])
    # Translate character stat table title to zh-CN
    translated_character_stat_table_title = []
    for stat_name in character_stat_table_title:
        translated_character_stat_table_title.append(character_stat_translator(stat_name))
    character_stat_table_list.append(translated_character_stat_table_title)
    num_of_character_stat = len(translated_character_stat_table_title)
    # Character Stat Table Body
    character_stat_data_elements = character_stat_table.find_element(By.TAG_NAME, "tbody") \
        .find_elements(By.TAG_NAME, "tr")
    for tr_row in character_stat_data_elements:
        this_tr_row = tr_row.find_elements(By.TAG_NAME, "td")
        character_stat_data = list([x.text for x in this_tr_row])
        # if "+" not in character_stat_data[0]:
        character_stat_table_list.append(character_stat_data[0:num_of_character_stat])
    # Character Skill Table
    character_skill_table = entire_table_area.find_element(By.ID, "char_skills")
    character_skill_title_list = character_skill_table.find_elements(By.CSS_SELECTOR, "span ~ table")
    talent_index = 0
    # Character Normal Attack Table
    character_normal_attack = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "td")
    normal_attack_stat_table_list = []
    character_normal_attack_img_url = character_normal_attack[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    character_normal_attack_name = character_normal_attack[1].text
    character_normal_attack_description = character_normal_attack[2].text
    character_normal_attack_stat_table = character_skill_title_list[0] \
        .find_element(By.CSS_SELECTOR, "table.genshin_table.skill_dmg_table").find_elements(By.TAG_NAME, "tr")
    for row in character_normal_attack_stat_table:
        this_row_data = row.find_elements(By.TAG_NAME, "td")
        normal_attack_stat_table_list.append(list([x.text for x in this_row_data]))
    talent_index += 1
    # Character E talent
    character_e_talent = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_e_talent_name = character_e_talent[0].text
    character_e_talent_img_url = character_e_talent[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    character_e_talent_description = character_e_talent[1].text
    character_e_talent_stat_table = character_e_talent[2].find_elements(By.TAG_NAME, "tr")
    character_e_talent_table_list = []
    for row in character_e_talent_stat_table:
        this_row_data = row.find_elements(By.TAG_NAME, "td")
        character_e_talent_table_list.append(list([x.text for x in this_row_data]))
    talent_index += 1
    # Character Special Talent
    if this_character_key_name == "ayaka" or this_character_key_name == "mona":
        character_special_talent = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
        character_special_talent_name = character_special_talent[0].text
        character_special_talent_img_url = character_special_talent[0].find_element(By.TAG_NAME, "img") \
            .get_attribute("src")
        character_special_talent_description = character_special_talent[1].text
        character_special_talent_stat_table = character_special_talent[2].find_elements(By.TAG_NAME, "tr")
        character_special_talent_table_list = []
        for row in character_special_talent_stat_table:
            this_row_data = row.find_elements(By.TAG_NAME, "td")
            character_special_talent_table_list.append(list([x.text for x in this_row_data]))
        talent_index += 1
    # Character Q Talent
    character_q_talent = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_q_talent_name = character_q_talent[0].text
    character_q_talent_img_url = character_q_talent[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    character_q_talent_description = character_q_talent[1].text
    character_q_talent_stat_table = character_q_talent[2].find_elements(By.TAG_NAME, "tr")
    character_q_talent_table_list = []
    for row in character_q_talent_stat_table:
        this_row_data = row.find_elements(By.TAG_NAME, "td")
        character_q_talent_table_list.append(list([x.text for x in this_row_data]))
    talent_index += 1
    # Passive Skill Table
    passive_skill1 = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    passive_skill1_name = passive_skill1[0].text
    passive_skill1_img_url = passive_skill1[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    passive_skill1_description = passive_skill1[1].text
    talent_index += 1
    passive_skill2 = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    passive_skill2_name = passive_skill2[0].text
    passive_skill2_img_url = passive_skill2[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    passive_skill2_description = passive_skill2[1].text
    talent_index += 1
    passive_skill3 = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    passive_skill3_name = passive_skill3[0].text
    passive_skill3_img_url = passive_skill3[0].find_element(By.TAG_NAME, "img").get_attribute("src")
    passive_skill3_description = passive_skill3[1].text
    talent_index += 1
    # shougun fix
    if this_character_key_name == "shougun" or this_character_key_name == "kokomi":
        passive_skill4 = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
        passive_skill4_name = passive_skill4[0].text
        passive_skill4_img_url = passive_skill4[0].find_element(By.TAG_NAME, "img").get_attribute("src")
        passive_skill4_description = passive_skill4[1].text
        talent_index += 1
    # Character Constellations Table
    character_constellation1_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation1_name = character_constellation1_table[0].text
    character_constellation1_img_url = character_constellation1_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation1_description = character_constellation1_table[1].text
    talent_index += 1
    character_constellation2_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation2_name = character_constellation2_table[0].text
    character_constellation2_img_url = character_constellation2_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation2_description = character_constellation2_table[1].text
    talent_index += 1
    character_constellation3_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation3_name = character_constellation3_table[0].text
    character_constellation3_img_url = character_constellation3_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation3_description = character_constellation3_table[1].text
    talent_index += 1
    character_constellation4_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation4_name = character_constellation4_table[0].text
    character_constellation4_img_url = character_constellation4_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation4_description = character_constellation4_table[1].text
    talent_index += 1
    character_constellation5_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation5_name = character_constellation5_table[0].text
    character_constellation5_img_url = character_constellation5_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation5_description = character_constellation5_table[1].text
    talent_index += 1
    character_constellation6_table = character_skill_title_list[talent_index].find_elements(By.TAG_NAME, "tr")
    character_constellation6_name = character_constellation6_table[0].text
    character_constellation6_img_url = character_constellation6_table[0].find_element(By.TAG_NAME, "img") \
        .get_attribute("src")
    character_constellation6_description = character_constellation6_table[1].text
    # Character Pictures
    character_gallery = character_page_driver.find_element(By.ID, "char_gallery")
    character_gallery_img_list = character_gallery.find_elements(By.CSS_SELECTOR, "div.gallery_cont")
    face_img_url = character_gallery_img_list[0].find_element(By.TAG_NAME, "a").get_attribute("href")
    gacha_card_img_url = character_gallery_img_list[2].find_element(By.TAG_NAME, "a").get_attribute("href")
    gacha_splash_img_url = character_gallery_img_list[3].find_element(By.TAG_NAME, "a").get_attribute("href")

    # Character Name Card
    character_related_items_area = character_page_driver.find_element(By.ID, "char_related_items")
    character_related_items = character_related_items_area.find_element(By.CSS_SELECTOR, "div.scroll_wrap") \
        .find_elements(By.TAG_NAME, "tr")
    character_profile_name_card_img_url = de_optimized_image_url(
        character_related_items[2].find_elements(By.TAG_NAME, "td")[0] \
            .find_element(By.TAG_NAME, "img").get_attribute("src")).replace(".png", "_profile.png")

    # Change result type
    if character_rarity == 4:
        star_url = "https://genshin.honeyhunterworld.com/img/back/item/4star.png"
    elif character_rarity == 5:
        star_url = "https://genshin.honeyhunterworld.com/img/back/item/5star.png"
    else:
        raise Exception("Invalid character rarity")
    # Write to dictionary
    this_character_dict = {
        "beta": False,
        "timestamp": str(int(time.time())),
        "Element": de_optimized_image_url(character_element_url),
        "Key": this_character_key_name,
        "City": getCharacterCity(this_character_key_name),
        "Star": de_optimized_image_url(star_url),
        "Name": character_name,
        "Talent": {
            "Name": character_talent_materials_name,
            "City": getTalentCity(character_talent_materials_name),
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_talent_materials_img_url)
        },
        "Boss": {
            "Name": character_boss_materials_name,
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_boss_materials_img_url)
        },
        "GemStone": {
            "Name": character_gemstone_materials_name,
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_gemstone_materials_img_url)
        },
        "Local": {
            "Name": character_local_materials_name,
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_local_materials_img_url)
        },
        "Monster": {
            "Name": character_monster_materials_name,
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_monster_materials_img_url)
        },
        "Weekly": {
            "Name": character_weekly_materials_name,
            "City": getWeeklyItemName(character_weekly_materials_name),
            "Star": "https://genshin.honeyhunterworld.com/img/back/item/4star.png",
            "Source": de_optimized_image_url(character_weekly_materials_img_url)
        }
    }
    character_stat_list = []
    for stat_index in range(0, len(character_stat_table_list[0])):
        this_stat_dict = {}
        this_stat_name = character_stat_table_list[0][stat_index]
        if this_stat_name != "Lv":
            for i in range(1, len(character_stat_table_list)):
                this_stat_value = character_stat_table_list[i][stat_index]
                this_stat_dict[str(character_stat_table_list[i][0])] = this_stat_value
            character_stat_list.append({
                "Name": this_stat_name,
                "Values": this_stat_dict
            })
    this_character_dict["CharStat"] = character_stat_list
    # Normal Attack
    normal_attack_dict = {
        "Name": character_normal_attack_name,
        "Source": de_optimized_image_url(character_normal_attack_img_url),
        "Description": character_normal_attack_description
    }
    normal_attack_stat_list = []
    for stat_index in range(0, len(normal_attack_stat_table_list)):
        this_stat_dict = {}
        this_stat_name = normal_attack_stat_table_list[stat_index][0]
        if this_stat_name != "":
            for i in range(1, len(normal_attack_stat_table_list[stat_index])):
                this_stat_value = normal_attack_stat_table_list[stat_index][i]
                this_stat_dict[str(normal_attack_stat_table_list[0][i])] = this_stat_value
            normal_attack_stat_list.append({
                "Name": this_stat_name,
                "Values": this_stat_dict
            })
    normal_attack_dict["Table"] = normal_attack_stat_list
    this_character_dict["NormalAttack"] = normal_attack_dict
    # Talent E
    talent_e_dict = {
        "Name": character_e_talent_name,
        "Source": de_optimized_image_url(character_e_talent_img_url),
        "Description": character_e_talent_description
    }
    talent_e_stat_list = []
    for stat_index in range(0, len(character_e_talent_table_list)):
        this_stat_dict = {}
        this_stat_name = character_e_talent_table_list[stat_index][0]
        if this_stat_name != "":
            for i in range(1, len(character_e_talent_table_list[stat_index])):
                this_stat_value = character_e_talent_table_list[stat_index][i]
                this_stat_dict[str(character_e_talent_table_list[0][i])] = this_stat_value
            talent_e_stat_list.append({
                "Name": this_stat_name,
                "Values": this_stat_dict
            })
    talent_e_dict["Table"] = talent_e_stat_list
    this_character_dict["TalentE"] = talent_e_dict
    # Talent Q
    talent_q_dict = {
        "Name": character_q_talent_name,
        "Source": de_optimized_image_url(character_q_talent_img_url),
        "Description": character_q_talent_description
    }
    talent_q_stat_list = []
    for stat_index in range(0, len(character_q_talent_table_list)):
        this_stat_dict = {}
        this_stat_name = character_q_talent_table_list[stat_index][0]
        if this_stat_name != "":
            for i in range(1, len(character_q_talent_table_list[stat_index])):
                this_stat_value = character_q_talent_table_list[stat_index][i]
                this_stat_dict[str(character_q_talent_table_list[0][i])] = this_stat_value
            talent_q_stat_list.append({
                "Name": this_stat_name,
                "Values": this_stat_dict
            })
    talent_q_dict["Table"] = talent_q_stat_list
    this_character_dict["TalentQ"] = talent_q_dict
    # All passives talent
    passive_talents_list = []
    # Special Talent (considered as Passive Talent)
    if character_special_talent_name != "":
        special_talent_dict = {
            "Name": character_special_talent_name,
            "Source": de_optimized_image_url(character_special_talent_img_url),
            "Description": character_special_talent_description
        }
        special_talent_stat_list = []
        for stat_index in range(0, len(character_special_talent_table_list)):
            this_stat_dict = {}
            this_stat_name = character_special_talent_table_list[stat_index][0]
            if this_stat_name != "":
                for i in range(1, len(character_special_talent_table_list[stat_index])):
                    this_stat_value = character_special_talent_table_list[stat_index][i]
                    this_stat_dict[str(character_special_talent_table_list[0][i])] = this_stat_value
                special_talent_stat_list.append({
                    "Name": this_stat_name,
                    "Values": this_stat_dict
                })
        special_talent_dict["Table"] = special_talent_stat_list
        passive_talents_list.append(special_talent_dict)
    # Passive Talents
    passive_talents_list.append({
        "Name": passive_skill1_name,
        "Source": de_optimized_image_url(passive_skill1_img_url),
        "Description": passive_skill1_description
    })
    passive_talents_list.append({
        "Name": passive_skill2_name,
        "Source": de_optimized_image_url(passive_skill2_img_url),
        "Description": passive_skill2_description
    })
    passive_talents_list.append({
        "Name": passive_skill3_name,
        "Source": de_optimized_image_url(passive_skill3_img_url),
        "Description": passive_skill3_description
    })
    if this_character_key_name == "shougun" or this_character_key_name == "kokomi":
        passive_talents_list.append({
            "Name": passive_skill4_name,
            "Source": de_optimized_image_url(passive_skill4_img_url),
            "Description": passive_skill4_description
        })
    this_character_dict["PassiveTalents"] = passive_talents_list
    # Constellation
    constellation_dict = {
        "Constellation1": {
            "Name": character_constellation1_name,
            "Source": de_optimized_image_url(character_constellation1_img_url),
            "Description": character_constellation1_description
        },
        "Constellation2": {
            "Name": character_constellation2_name,
            "Source": de_optimized_image_url(character_constellation2_img_url),
            "Description": character_constellation2_description
        },
        "Constellation3": {
            "Name": character_constellation3_name,
            "Source": de_optimized_image_url(character_constellation3_img_url),
            "Description": character_constellation3_description
        },
        "Constellation4": {
            "Name": character_constellation4_name,
            "Source": de_optimized_image_url(character_constellation4_img_url),
            "Description": character_constellation4_description
        },
        "Constellation5": {
            "Name": character_constellation5_name,
            "Source": de_optimized_image_url(character_constellation5_img_url),
            "Description": character_constellation5_description
        },
        "Constellation6": {
            "Name": character_constellation6_name,
            "Source": de_optimized_image_url(character_constellation6_img_url),
            "Description": character_constellation6_description
        }
    }
    this_character_dict["Constellation"] = constellation_dict
    this_character_dict["Title"] = character_title
    this_character_dict["Description"] = character_description
    this_character_dict["AstrolabeName"] = character_constellation
    this_character_dict["Profile"] = character_profile_name_card_img_url
    this_character_dict["Source"] = de_optimized_image_url(face_img_url)
    this_character_dict["GachaCard"] = de_optimized_image_url(gacha_card_img_url)
    this_character_dict["GachaSplash"] = de_optimized_image_url(gacha_splash_img_url)

    character_page_driver.close()
    return this_character_dict


if __name__ == "__main__":
    start_time = int(time.time())
    result_list = []
    # Load main page
    driver = GetChrome()
    driver.get("https://genshin.honeyhunterworld.com/fam_chars/?lang=CHS")
    time.sleep(4)
    # Click to expand all characters
    items_per_page_selection = Select(
        driver.find_element(By.XPATH, r'//*[@id="characters"]/table/tbody/tr/td[1]/select'))
    items_per_page_selection.select_by_visible_text("100")
    # Load table data
    table_element = driver.find_element(By.ID, "characters").find_element(By.CSS_SELECTOR, "div.scroll_wrap")\
        .find_element(By.CSS_SELECTOR, "table").find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
    print(len(table_element))
    for i in range(len(table_element)):
        this_row = table_element[i].find_elements(By.TAG_NAME, 'td')
        this_row_character_name = this_row[1].text
        # Skip traveler's data
        if this_row_character_name == "旅行者":
            continue
        this_character_detail_url = this_row[0].find_element(By.TAG_NAME, 'a').get_attribute('href').strip()
        print(this_character_detail_url)
        # Load character detail page via sub-webdriver
        result = fetch_character_data(this_character_detail_url)
        result_list.append(result)

    try:
        result_list = json.dumps(result_list, ensure_ascii=False, indent=4, separators=(',', ':'))
        new_file_name = "characters-" + str(int(time.time())) + ".json"
        f_output = open(new_file_name, mode="w+", encoding='utf-8')
        f_output.write(result_list)
        f_output.close()
    except Exception as e:
        print(e)

    driver.close()
    end_time = int(time.time())
    print("\nTask finished. Total time: " + str(end_time - start_time) + " seconds")
