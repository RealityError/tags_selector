import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import random
from config import config, load_config

class CharacterSelector:
    def __init__(self, csv_path: str, config: dict):
        """
        初始化角色选择器
        csv_path: 角色CSV文件的路径
        config: 配置字典
        """
        self.csv_path = csv_path
        self.characters_df = None
        self._load_csv()
        
        # 检查配置是否有效
        if not config or 'character_selector' not in config:
            raise ValueError("配置无效：缺少 character_selector 配置项")
        
        required_config = ['min_count', 'max_count', 'min_weight', 'max_weight', 
                         'min_total_works', 'min_solo_works']
        missing_config = [item for item in required_config if item not in config['character_selector']]
        
        if missing_config:
            raise ValueError(f"配置缺少必要的项目: {', '.join(missing_config)}")
            
        self.config = config
    
    def _load_csv(self):
        """加载并处理CSV文件"""
        try:
            self.characters_df = pd.read_csv(self.csv_path)
            # 必需的基本列
            required_columns = ['character', 'copyright', 'trigger', 'count', 'solo_count', 'url']
            missing_columns = [col for col in required_columns if col not in self.characters_df.columns]
            if missing_columns:
                raise Exception(f"{self.csv_path} CSV文件缺少必要的列: {', '.join(missing_columns)}")
            
            # 处理 core_tags 列
            if 'core_tags' in self.characters_df.columns:
                # 将字符串格式的标签列表转换为实际的列表
                self.characters_df['core_tags'] = self.characters_df['core_tags'].apply(
                    lambda x: x.split(',') if isinstance(x, str) and x.strip() else []
                )
                print(f"{self.csv_path} 已加载 core_tags 列")
            else:
                self.characters_df['core_tags'] = [[]] * len(self.characters_df)
                print(f"{self.csv_path} CSV文件中没有 core_tags 列，将使用空标签列表")
            
        except Exception as e:
            raise Exception(f"读取{self.csv_path} CSV文件失败: {e}")
    
    def update_config(self):
        """更新配置"""
        self.config = load_config('config.yaml')
    
    def select_characters(self, 
                         min_count: int = None, 
                         max_count: int = None,
                         min_weight: float = None,
                         max_weight: float = None,
                         min_total_works: int = None,
                         min_solo_works: int = None,
                         copyright_filter: List[str] = None,
                         mode: str = None) -> List[Tuple[str, float, List[str]]]:
        """
        选择指定数量的角色并分配权重
        返回: [(触发词, 权重, core_tags)] 的列表
        """
        if min_count is None:
            min_count = self.config['character_selector']['min_count']
        if max_count is None:
            max_count = self.config['character_selector']['max_count']
        if min_weight is None:
            min_weight = self.config['character_selector']['min_weight']
        if max_weight is None:
            max_weight = self.config['character_selector']['max_weight']
        if min_total_works is None:
            min_total_works = self.config['character_selector']['min_total_works']
        if min_solo_works is None:
            min_solo_works = self.config['character_selector']['min_solo_works']
        
        mode = self.config['character_selector']['mode']
        
        if mode == "random":
            return self._select_characters_random(min_count, max_count, min_weight, max_weight,
                                               min_total_works, min_solo_works, copyright_filter)
        elif mode == "only":
            return self._select_characters_only(min_count, max_count, min_weight, max_weight,
                                             min_total_works, min_solo_works, copyright_filter)
        else:
            raise ValueError("无效的选取模式")
    
    def _select_characters_random(self, min_count: int, max_count: int,
                                min_weight: float, max_weight: float,
                                min_total_works: int, min_solo_works: int,
                                copyright_filter: List[str] = None) -> List[Tuple[str, float, List[str]]]:
        """随机选择模式"""
        if self.characters_df is None:
            raise Exception("CSV文件未加载")
            
        # 确保参数有效
        if min_count > max_count:
            raise ValueError("最小数量不能大于最大数量")
        if min_weight > max_weight:
            raise ValueError("最小权重不能大于最大权重")
            
        # 筛选角色
        valid_characters = self.characters_df[
            (self.characters_df['count'] >= min_total_works) &
            (self.characters_df['solo_count'] >= min_solo_works)
        ]
        
        # 如果指定了版权过滤
        if copyright_filter:
            valid_characters = valid_characters[
                valid_characters['copyright'].isin(copyright_filter)
            ]
        
        if valid_characters.empty:
            raise ValueError(f"没有找到符合条件的角色")
            
        # 随机选择角色数量
        count = min(random.randint(min_count, max_count), len(valid_characters))
        
        # 随机选择角色
        selected_characters = valid_characters.sample(n=count)
        
        # 为每个角色分配随机权重
        result = []
        for _, character in selected_characters.iterrows():
            weight = round(random.uniform(min_weight, max_weight), 2)
            core_tags = character['core_tags'] if isinstance(character['core_tags'], list) else []
            result.append((character['trigger'], weight, core_tags))
        
        print(f"\n[Random模式] {self.csv_path} 总角色数: {len(self.characters_df)}, "
              f"符合条件角色数: {len(valid_characters)}, "
              f"本次选择: {count}")
        return result
    
    def _select_characters_only(self, min_count: int, max_count: int,
                              min_weight: float, max_weight: float,
                              min_total_works: int, min_solo_works: int,
                              copyright_filter: List[str] = None) -> List[Tuple[str, float, List[str]]]:
        """唯一选择模式"""
        if not hasattr(self, '_used_characters'):
            self._used_characters = set()
        
        if self.characters_df is None:
            raise Exception("CSV文件未加载")
            
        # 确保参数有效
        if min_count > max_count:
            raise ValueError("最小数量不能大于最大数量")
        if min_weight > max_weight:
            raise ValueError("最小权重不能大于最大权重")
            
        # 筛选角色
        all_valid_characters = self.characters_df[
            (self.characters_df['count'] >= min_total_works) &
            (self.characters_df['solo_count'] >= min_solo_works)
        ]
        
        # 如果指定了版权过滤
        if copyright_filter:
            all_valid_characters = all_valid_characters[
                all_valid_characters['copyright'].isin(copyright_filter)
            ]
        
        valid_characters = all_valid_characters[
            ~all_valid_characters['trigger'].isin(self._used_characters)
        ]
        
        # 如果没有更多可用的角色，重置已使用列表
        if valid_characters.empty:
            self._used_characters.clear()
            print(f"\n[Only模式] {self.csv_path} 已用完所有角色，重置选择列表")
            valid_characters = all_valid_characters
        
        if valid_characters.empty:
            raise ValueError(f"没有找到符合条件的角色")
            
        # 随机选择角色数量
        count = min(random.randint(min_count, max_count), len(valid_characters))
        
        # 随机选择角色
        selected_characters = valid_characters.sample(n=count)
        
        # 为每个角色分配随机权重并记录已使用
        result = []
        for _, character in selected_characters.iterrows():
            weight = round(random.uniform(min_weight, max_weight), 2)
            trigger = character['trigger']
            core_tags = character['core_tags'] if isinstance(character['core_tags'], list) else []
            result.append((trigger, weight, core_tags))
            self._used_characters.add(trigger)
        
        print(f"\n[Only模式] {self.csv_path} 总角色数: {len(self.characters_df)}, "
              f"符合条件角色数: {len(all_valid_characters)}, "
              f"当前可选角色数: {len(valid_characters)}, "
              f"已使用角色数: {len(self._used_characters)}, "
              f"本次选择: {count}")
        return result
    
    def reset_used_characters(self):
        """重置已使用的角色列表"""
        if hasattr(self, '_used_characters'):
            self._used_characters.clear()
    
    def get_available_copyrights(self, min_total_works: int = 0) -> List[str]:
        """获取可用的作品系列列表"""
        if self.characters_df is None:
            raise Exception("CSV文件未加载")
            
        # 按版权分组并计算每个版权的总作品数
        copyright_counts = self.characters_df.groupby('copyright')['count'].sum()
        # 筛选出符合最小作品数的版权
        valid_copyrights = copyright_counts[copyright_counts >= min_total_works]
        
        return sorted(valid_copyrights.index.tolist())

if __name__ == "__main__":
    # 在循环外创建选择器实例
    selector = CharacterSelector('danbooru_character_webui.csv', config)
    while True:
        try:
            result = selector.select_characters()
            print(result)
            input("\n按回车继续...")  # 添加暂停，方便查看结果
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"发生错误: {e}")
            break 