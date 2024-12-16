from artists_selector import ArtistSelector
from character_selector import CharacterSelector

from config import config
# 设置日志


def main():
    """主程序"""
    

    # 初始化选择器
    selector_artist_danbooru = ArtistSelector("danbooru_artist_webui.csv", config)
    selector_character_danbooru = CharacterSelector("danbooru_character_webui.csv", config)
    selector_artist_e621 = ArtistSelector("e621_artist_webui.csv", config)
    selector_character_e621 = CharacterSelector("e621_character_webui.csv", config)
    
    while True:
        text = input("按回车继续...")
        if text == "reset":
            selector_artist_danbooru.reset_used_artists()
            selector_character_danbooru.reset_used_characters()
            selector_artist_e621.reset_used_artists()
            selector_character_e621.reset_used_characters()
            print("已重置已使用画师和角色")
            continue

        # 选择danbooru画师
        selected_artists_danbooru = selector_artist_danbooru.select_artists()
        # 选择danbooru角色
        selected_characters_danbooru = selector_character_danbooru.select_characters()
        # 选择e621画师
        selected_artists_e621 = selector_artist_e621.select_artists()
        # 选择e621角色
        selected_characters_e621 = selector_character_e621.select_characters()
        
        # 输出结果
        print("danbooru画师: ", selected_artists_danbooru)
        print("danbooru角色: ", selected_characters_danbooru)
        print("e621画师: ", selected_artists_e621)
        print("e621角色: ", selected_characters_e621)


if __name__ == "__main__":
    main() 