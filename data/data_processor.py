import os
import pandas as pd
import wbdata
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorldBankDataProcessor:
    def __init__(self, start_date='2010-01-01', end_date='2022-12-31'):
        """
        初始化数据处理器
        
        Args:
            start_date (str): 开始日期
            end_date (str): 结束日期
        """
        self.start_date_str = start_date # Store original string for logging or other uses
        self.end_date_str = end_date
        self.start_year = datetime.strptime(start_date, '%Y-%m-%d').year
        self.end_year = datetime.strptime(end_date, '%Y-%m-%d').year
        self.data_dir = os.path.join(os.path.dirname(__file__), 'processed')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 恢复原始指标列表，我们将逐个测试它们
        self.indicators = {
            'NY.GDP.PCAP.KD': 'GDP_per_capita',
            'SP.DYN.LE00.IN': 'life_expectancy',
            'SE.ENR.TERT.FM.ZS': 'tertiary_education',
            'EN.ATM.CO2E.PC': 'co2_emissions',
            'SP.POP.TOTL': 'population',
            'SE.ENR.PRSC.FM.ZS': 'primary_education',
            'SH.MED.BEDS.ZS': 'hospital_beds',
            'IT.NET.USER.ZS': 'internet_users'
        }

    def fetch_data(self, countries=None):
        logger.info(f"开始获取世界银行数据，年份范围: {self.start_year}-{self.end_year}")
        date_tuple = (str(self.start_year), str(self.end_year))
        source_id = 2
        
        # 确定要获取的国家列表
        # 如果 countries is None (来自main的默认调用), 我们还是用USA进行诊断性单国家获取
        # 如果要切换到获取所有国家, main() 中应该调用 processor.fetch_data(countries='all') 或 processor.fetch_data(countries=['all'])
        # 或者根据 wbdata 文档， countries=None 可能就代表所有国家。
        # 为了保持当前成功的诊断流程，我们暂时固定为USA，除非明确传入其他国家。
        # 如果要恢复“所有国家”或动态国家列表，需要调整此处的 country_list_to_fetch
        
        if countries is None:
            logger.info("诊断模式: 未指定国家，将使用 ['USA'] 进行单国家获取。")
            country_list_to_fetch = ['USA']
        elif isinstance(countries, str) and countries.lower() == 'all':
             logger.info("获取模式: 请求所有国家数据 ('all')。注意：这可能导致API错误，如果组合无效。")
             country_list_to_fetch = ['all'] # 或者根据wbdata文档，可能是其他特定值或None
        elif isinstance(countries, list):
            country_list_to_fetch = countries
        else: # 单个国家字符串的情况
            country_list_to_fetch = [countries]

        # 当前的单国家处理逻辑主要针对 fetch_data 内部迭代单个指标时
        # 如果 country_list_to_fetch 包含 'all' 或者多个国家, wbdata.get_dataframe 的行为会不同
        # df_indicator.reset_index() 之后可能会直接包含 'country' 列
        # 因此，下面的手动添加 'country_code' 的逻辑主要适用于我们迭代获取单国家数据的情况
        is_single_country_iterative_fetch = len(country_list_to_fetch) == 1 and country_list_to_fetch[0].lower() != 'all'
        single_country_code_if_iterative = country_list_to_fetch[0] if is_single_country_iterative_fetch else None

        logger.info(f"目标国家列表: {country_list_to_fetch}")

        collected_valid_dfs = [] 
        problematic_indicators_info = {}

        # 如果我们不是请求 'all' 并且国家列表多于1个，或者就是 'all'
        # 那么我们应该尝试一次性获取所有指标，而不是逐个迭代（除非wbdata本身对多指标单次请求有限制）
        # 为简化，我们暂时保持逐个指标获取的诊断模式，即使country_list_to_fetch可能是['all']
        # 这有助于隔离是哪个指标在 'all' 国家下出问题

        for indicator_code, indicator_name in self.indicators.items():
            logger.info(f"获取指标 -> {indicator_name} ({indicator_code}) for {country_list_to_fetch}, source {source_id}, date {date_tuple}")
            current_indicator_dict = {indicator_code: indicator_name}
            try:
                df_indicator = wbdata.get_dataframe(
                    current_indicator_dict,
                    country=country_list_to_fetch, # 现在使用实际要获取的国家列表
                    date=date_tuple,
                    source=source_id
                )
                
                if df_indicator.empty:
                    logger.warning(f"指标 {indicator_name} ({indicator_code}) 获取到的数据为空 (无API错误)。")
                    problematic_indicators_info[indicator_code] = f"Data was empty for {indicator_name}"
                else:
                    logger.info(f"成功获取指标 {indicator_name} ({indicator_code}) - {len(df_indicator)} 条记录。列: {df_indicator.columns.tolist()}")
                    df_indicator = df_indicator.reset_index() 
                    logger.info(f"指标 {indicator_name} reset_index后列: {df_indicator.columns.tolist()}")

                    if 'date' not in df_indicator.columns:
                        err_msg = f"指标 {indicator_name} ({indicator_code}) 返回的数据缺少 'date' 列。无法处理。列: {df_indicator.columns.tolist()}"
                        logger.error(f"{err_msg}")
                        problematic_indicators_info[indicator_code] = err_msg
                        continue 
                    
                    if 'country' not in df_indicator.columns:
                        if is_single_country_iterative_fetch and single_country_code_if_iterative:
                            logger.info(f"指标 {indicator_name} 数据中无 'country' 列 (单国家请求)，手动添加 'country_code': {single_country_code_if_iterative}")
                            df_indicator['country_code'] = single_country_code_if_iterative
                        else:
                            # 如果不是预期的单国家无country列情况（比如请求了'all'但仍然没有country列），则记录问题
                            err_msg = f"指标 {indicator_name} 数据中无 'country' 列，且不符合单国家获取的预期。列: {df_indicator.columns.tolist()}"
                            logger.error(f"{err_msg}")
                            problematic_indicators_info[indicator_code] = err_msg
                            continue
                    else:
                        df_indicator = df_indicator.rename(columns={'country': 'country_code'})
                    
                    if 'country_code' in df_indicator.columns and 'date' in df_indicator.columns:
                        df_indicator = df_indicator.rename(columns={'date': 'year_str'})
                        if indicator_name not in df_indicator.columns:
                            potential_value_cols = [col for col in df_indicator.columns if col not in ['country_code', 'year_str']]
                            if len(potential_value_cols) == 1:
                                logger.warning(f"指标 {indicator_name} 的值列似乎是 '{potential_value_cols[0]}' 而不是预期的 '{indicator_name}'。将使用它并重命名。")
                                df_indicator = df_indicator.rename(columns={potential_value_cols[0]: indicator_name})
                            else:
                                err_msg = f"指标 {indicator_name} 的值列无法明确识别。可用列: {df_indicator.columns.tolist()}"
                                logger.error(f"{err_msg}")
                                problematic_indicators_info[indicator_code] = err_msg
                                continue

                        df_indicator = df_indicator.set_index(['country_code', 'year_str'])
                        collected_valid_dfs.append(df_indicator)
                        logger.info(f"指标 {indicator_name} 处理完毕并添加到待合并列表。索引: {df_indicator.index.names}, 列: {df_indicator.columns.tolist()}")
                    else:
                        err_msg = f"指标 {indicator_name} 在处理后仍缺少 'country_code' 或 'year_str'。列: {df_indicator.columns.tolist()}"
                        logger.error(f"{err_msg}")
                        problematic_indicators_info[indicator_code] = err_msg
                                
            except Exception as e:
                error_message = f"获取指标 {indicator_name} ({indicator_code}) 时发生严重错误: {str(e)}"
                logger.error(f"{error_message}")
                problematic_indicators_info[indicator_code] = error_message
        
        if problematic_indicators_info:
            logger.warning("总结: 以下指标在单独获取或处理时遇到问题:")
            for code, err_msg in problematic_indicators_info.items():
                logger.warning(f"  - {self.indicators.get(code, code)} ({code}): {err_msg}")

        if not collected_valid_dfs:
            logger.error("未能收集到任何可供合并的有效指标数据。数据获取流程终止。")
            return None

        logger.info(f"成功获取并初步处理了 {len(collected_valid_dfs)} 个指标的DataFrame。现在尝试合并它们...")
        
        final_df = None
        if len(collected_valid_dfs) == 1:
            final_df = collected_valid_dfs[0].reset_index()
        elif len(collected_valid_dfs) > 1:
            final_df = collected_valid_dfs[0] 
            for i in range(1, len(collected_valid_dfs)):
                final_df = pd.merge(final_df, collected_valid_dfs[i], on=['country_code', 'year_str'], how='outer')
            final_df = final_df.reset_index()
        
        if final_df is None or final_df.empty:
            logger.error("合并后的DataFrame为空或合并失败。")
            return None
            
        logger.info(f"成功合并数据，最终得到 {len(final_df)} 条记录，包含 {len(final_df.columns)} 列。列名: {final_df.columns.tolist()}")
        raw_data_path = os.path.join(self.data_dir, 'world_bank_raw_data.csv') # 更通用的文件名
        final_df.to_csv(raw_data_path, index=False)
        logger.info(f"合并后的原始数据已保存至: {raw_data_path}")        
        return final_df

    def preprocess_data(self, df):
        """
        预处理数据
        
        Args:
            df (DataFrame): 原始数据框
        """
        try:
            if df is None or df.empty:
                logger.error("没有数据可供处理")
                return None
                
            logger.info("开始预处理数据...")
            
            # 使用 df.ffill() 替换已弃用的 fillna(method='ffill')
            df = df.ffill()
            
            # 'year_str' 列是从 wbdata 获取的年份字符串，将其转换为数字年份 'year'
            if 'year_str' in df.columns:
                df['year'] = pd.to_numeric(df['year_str'], errors='coerce')
                df.dropna(subset=['year'], inplace=True) # 移除转换失败的行
                df['year'] = df['year'].astype(int)
            else:
                logger.error("预处理错误: 缺少 'year_str' 列，无法创建数字 'year' 列。")
                # 如果没有年份信息，后续的 pct_change 会很困难或无意义
                return df # 或者返回None，取决于错误处理策略

            # 计算年度变化率 (yoy - year over year)
            # 确保在计算yoy之前，数据是按国家和年份排序的
            if 'country_code' in df.columns and 'year' in df.columns:
                df = df.sort_values(by=['country_code', 'year'])
                for indicator_col_name in self.indicators.values(): # 使用 self.indicators 中的自定义名称
                    if indicator_col_name in df.columns:
                        if pd.api.types.is_numeric_dtype(df[indicator_col_name]):
                            # 指定 fill_method=None 来消除 FutureWarning
                            df[f'{indicator_col_name}_yoy'] = df.groupby('country_code', group_keys=False)[indicator_col_name].pct_change(fill_method=None) * 100
                        else:
                            logger.warning(f"指标列 {indicator_col_name} 不是数值类型 (类型: {df[indicator_col_name].dtype})，跳过YOY计算。")
                    else:
                        # 这个指标可能在获取阶段就失败了，或者没有成功合并进来
                        logger.warning(f"指标列 {indicator_col_name} 在DataFrame中未找到，跳过YOY计算。")
            else:
                logger.warning("无法计算年增长率，因为缺少 'country_code' 或 'year' 列进行排序和分组。")

            # 保存处理后的数据
            processed_data_path = os.path.join(self.data_dir, 'world_bank_processed.csv')
            df.to_csv(processed_data_path, index=False)
            logger.info(f"处理后的数据已保存至: {processed_data_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"预处理数据时发生错误: {str(e)}")
            raise

    def get_country_list(self):
        """
        获取可用的国家列表
        """
        try:
            logger.info("开始获取国家列表...")
            countries_info = wbdata.get_countries() # Returns a list of dict-like objects
            
            data_for_df = []
            if not countries_info:
                logger.warning("wbdata.get_countries() 返回了空列表或None。")
                return pd.DataFrame() # 返回空的DataFrame

            for country_data in countries_info:
                if not isinstance(country_data, dict):
                    logger.warning(f"Expected a dict for country_data, but got {type(country_data)}. Skipping.")
                    continue

                region_info = country_data.get('region', {}) if isinstance(country_data.get('region'), dict) else {}
                income_level_info = country_data.get('incomeLevel', {}) if isinstance(country_data.get('incomeLevel'), dict) else {}
                lending_type_info = country_data.get('lendingType', {}) if isinstance(country_data.get('lendingType'), dict) else {}

                data_for_df.append({
                    'country_code': country_data.get('id'),
                    'country_name': country_data.get('name'),
                    'iso2Code': country_data.get('iso2Code'),
                    'region_id': region_info.get('id'),
                    'region_name': region_info.get('value'),
                    'income_level_id': income_level_info.get('id'),
                    'income_level': income_level_info.get('value'),
                    'lending_type_id': lending_type_info.get('id'),
                    'lending_type': lending_type_info.get('value'),
                    'capital_city': country_data.get('capitalCity'),
                    'longitude': country_data.get('longitude'),
                    'latitude': country_data.get('latitude')
                })
            
            if not data_for_df:
                logger.warning("未能从获取的国家信息中构建任何有效数据行。")
                return pd.DataFrame()

            country_df = pd.DataFrame(data_for_df)
            
            # 保存国家信息
            country_info_path = os.path.join(self.data_dir, 'country_info.csv')
            country_df.to_csv(country_info_path, index=False)
            logger.info(f"国家信息已保存至: {country_info_path}")
            
            return country_df
            
        except Exception as e:
            logger.error(f"获取国家列表时发生错误: {str(e)}")
            # raise # 根据需要决定是否重新抛出
            return pd.DataFrame() # 在出错时返回空的DataFrame，避免主流程因None而出错

def main():
    """
    主函数
    """
    try:
        # 创建数据处理器实例
        processor = WorldBankDataProcessor()
        
        # 获取国家列表
        countries_df = processor.get_country_list() 
        if countries_df is not None and not countries_df.empty:
            logger.info(f"获取到 {len(countries_df)} 个国家的信息")
        else:
            logger.warning("未能获取到国家列表，或列表为空。fetch_data 将默认使用USA。")
        
        # 默认调用 fetch_data() 将使用USA进行诊断。
        
        # 如果要获取所有国家: 
        df=processor.fetch_data(countries='all')
        # 或特定国家列表: processor.fetch_data(countries=['USA', 'CHN', 'IND'])
        # df = processor.fetch_data()  默认获取USA数据
        
        if df is not None and not df.empty:
            logger.info(f"数据获取完成，共获取到 {len(df)} 条数据记录。")
            
            # 预处理数据
            processed_df = processor.preprocess_data(df.copy()) # 使用 .copy() 避免 SettingWithCopyWarning
            if processed_df is not None and not processed_df.empty:
                logger.info("数据预处理完成。")
            else:
                logger.warning("数据预处理未能完成或返回空数据。")
        else:
            logger.error("未能获取到任何指标数据，或在获取过程中发生错误。请检查日志。")
        
    except Exception as e:
        logger.error(f"程序主流程执行过程中发生严重错误: {str(e)}")
        # raise # 可以选择是否重新抛出异常

if __name__ == "__main__":
    main() 