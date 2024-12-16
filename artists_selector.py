import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import random
from config import config,load_config

class ArtistSelector:
    def __init__(self, csv_path: str, config: dict):
        """
        初始化选择器
        csv_path: 画师CSV文件的路径
        config: 配置字典
        """
        self.csv_path = csv_path
        self.artists_df = None
        self._load_csv()
        
        # 检查配置是否有效
        if not config or 'artist_selector' not in config:
            raise ValueError("配置无效：缺少 artist_selector 配置项")
        
        required_config = ['min_count', 'max_count', 'min_weight', 'max_weight', 'min_works']
        missing_config = [item for item in required_config if item not in config['artist_selector']]
        
        if missing_config:
            raise ValueError(f"配置缺少必要的项目: {', '.join(missing_config)}")
            
        self.config = config

    def _load_csv(self):
        """加载并处理CSV文件"""
        try:
            # 指定列名
            self.artists_df = pd.read_csv(self.csv_path)
            # 确保必要的列存在
            required_columns = ['artist', 'trigger', 'count', 'url']
            missing_columns = [col for col in required_columns if col not in self.artists_df.columns]
            if missing_columns:
                raise Exception(f"{self.csv_path} CSV文件缺少必要的列: {', '.join(missing_columns)}")
        except Exception as e:
            raise Exception(f"读取{self.csv_path} CSV文件失败: {e}")
        
    def update_config(self):
        self.config = load_config('config.yaml')
    
    def select_artists(self,min_count:int=None,max_count:int=None,min_weight:float=None,max_weight:float=None,min_works:int=None,mode:str=None) -> List[Tuple[str, float]]:
        """
        选择指定数量的画师并分配权重
        min_count: 最少选择数量
        max_count: 最大选择数量
        min_weight: 最小权重
        max_weight: 最大权重
        min_works: 最小作品数量（可选）
        返回: [(触发词, 权重)] 的列表
        """
        if min_count is None:
            min_count = self.config['artist_selector']['min_count']
        if max_count is None:
            max_count = self.config['artist_selector']['max_count']
        if min_weight is None:
            min_weight = self.config['artist_selector']['min_weight']
        if max_weight is None:
            max_weight = self.config['artist_selector']['max_weight']
        if min_works is None:
            min_works = self.config['artist_selector']['min_works']
        
        mode = self.config['artist_selector']['mode']
        
        if mode == "random":
            return self._select_artists_random(min_count, max_count, min_weight, max_weight, min_works)
        elif mode == "only":
            return self._select_artists_only(min_count, max_count, min_weight, max_weight, min_works)
        else:
            raise ValueError("无效的选取模式")
        
    def _select_artists_random(self, min_count: int, max_count: int, min_weight: float, max_weight: float, min_works: int) -> List[Tuple[str, float]]:
        """随机选择模式"""
        if self.artists_df is None:
            raise Exception("CSV文件未加载")
        
        # 确保参数有效
        if min_count > max_count:
            raise ValueError("最小数量不能大于最大数量")
        if min_weight > max_weight:
            raise ValueError("最小权重不能大于最大权重")
        
        # 筛选画师
        valid_artists = self.artists_df[
            self.artists_df['count'] >= min_works
        ]
        
        if valid_artists.empty:
            raise ValueError(f"没有找到作品数量大于{min_works}的画师")
        
        # 随机选择画师数量
        count = min(random.randint(min_count, max_count), len(valid_artists))
        
        # 随机选择画师
        selected_artists = valid_artists.sample(n=count)
        
        # 为每个画师分配随机权重
        result = []
        for _, artist in selected_artists.iterrows():
            weight = round(random.uniform(min_weight, max_weight), 2)
            result.append((artist['trigger'], weight))
        
        print(f"\n[Random模式] {self.csv_path}总画师数: {len(self.artists_df)}, 符合条件画师数: {len(valid_artists)}, 本次选择: {count}")
        return result
    
    def _select_artists_only(self, min_count: int, max_count: int, min_weight: float, max_weight: float, min_works: int) -> List[Tuple[str, float]]:
        """唯一选择模式"""
        if not hasattr(self, '_used_artists'):
            self._used_artists = set()
        
        if self.artists_df is None:
            raise Exception("CSV文件未加载")
        
        # 确保参数有效
        if min_count > max_count:
            raise ValueError("最小数量不能大于最大数量")
        if min_weight > max_weight:
            raise ValueError("最小权重不能大于最大权重")
        
        # 筛选画师
        all_valid_artists = self.artists_df[self.artists_df['count'] >= min_works]
        valid_artists = all_valid_artists[~all_valid_artists['trigger'].isin(self._used_artists)]
        
        # 如果没有更多可用的画师，重置已使用列表
        if valid_artists.empty:
            self._used_artists.clear()
            print(f"\n[Only模式] {self.csv_path}已用完所有画师，重置选择列表")
            valid_artists = all_valid_artists
        
        if valid_artists.empty:
            raise ValueError(f"没有找到作品数量大于{min_works}的画师")
        
        # 随机选择画师数量
        count = min(random.randint(min_count, max_count), len(valid_artists))
        
        # 随机选择画师
        selected_artists = valid_artists.sample(n=count)
        
        # 为每个画师分配随机权重并记录已使用
        result = []
        for _, artist in selected_artists.iterrows():
            weight = round(random.uniform(min_weight, max_weight), 2)
            trigger = artist['trigger']
            result.append((trigger, weight))
            self._used_artists.add(trigger)
        
        print(f"\n[Only模式] {self.csv_path}总画师数: {len(self.artists_df)}, "
              f"符合条件画师数: {len(all_valid_artists)}, "
              f"当前可选画师数: {len(valid_artists)}, "
              f"已使用画师数: {len(self._used_artists)}, "
              f"本次选择: {count}")
        return result
    
    def reset_used_artists(self):
        """重置已使用的画师列表"""
        if hasattr(self, '_used_artists'):
            self._used_artists.clear()
    
    
    
if __name__ == "__main__":
    # 在循环外创建选择器实例
    selector = ArtistSelector('danbooru_artist_webui.csv', config)
    while True:
        try:
            # # 每次循环更新配置
            # selector.update_config()
            result = selector.select_artists()
            print(result)
            input("\n按回车继续...")  # 添加暂停，方便查看结果
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"发生错误: {e}")
            break
