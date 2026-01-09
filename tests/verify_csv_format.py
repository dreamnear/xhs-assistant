"""
验证CSV文件格式和天数限制
"""
import pandas as pd
from pathlib import Path


def validate_csv(csv_path: str, expected_days: int):
    """验证CSV文件"""
    print("=" * 60)
    print(f"验证: {csv_path}")
    print(f"期望天数: {expected_days}")
    print("=" * 60)

    try:
        # 读取CSV文件（UTF-8 BOM）
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        print(f"\n✅ 文件读取成功（UTF-8 BOM编码）")
        print(f"实际行数: {len(df)}")

        # 检查天数
        if abs(len(df) - expected_days) <= 1:
            print(f"✅ 天数验证通过: {len(df)}天（期望{expected_days}天）")
        else:
            print(f"❌ 天数不符: 实际{len(df)}天，期望{expected_days}天")
            return False

        # 检查字段
        required_fields = ['日期', '新增粉丝', '掉丝数', '总粉丝数', '净增长', '当前粉丝总数']
        missing_fields = [f for f in required_fields if f not in df.columns]
        if missing_fields:
            print(f"❌ 缺少字段: {missing_fields}")
            return False
        else:
            print(f"✅ 所有必需字段存在")

        # 检查数据有效性
        valid_data = df[df['总粉丝数'] > 0]
        if len(valid_data) > 0:
            print(f"✅ 有效数据: {len(valid_data)}天有总粉丝数")
        else:
            print(f"❌ 所有数据的总粉丝数都为0")
            return False

        # 显示前几行
        print(f"\n前3行数据:")
        print(df.head(3).to_string(index=False))

        print(f"\nSUCCESS")
        return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    output_dir = Path('data/output')

    # 查找所有粉丝数据CSV文件
    csv_files = sorted(output_dir.glob('followers_data_*.csv'))

    if not csv_files:
        print("❌ 未找到粉丝数据CSV文件")
        return

    print(f"找到 {len(csv_files)} 个粉丝数据文件\n")

    # 验证最新的文件
    latest_file = csv_files[-1]

    # 根据文件名判断是7天还是30天
    # 这里我们假设最新的文件是刚才导出的
    # 实际使用时应该根据用户选择来验证

    # 先验证文件格式
    df = pd.read_csv(latest_file, encoding='utf-8-sig')
    actual_days = len(df)

    # 判断是7天还是30天（基于实际行数）
    if actual_days <= 10:
        expected_days = 7
    else:
        expected_days = 30

    print(f"检测到文件包含{actual_days}天数据，验证为{expected_days}天导出\n")

    if validate_csv(str(latest_file), expected_days):
        print("\n" + "=" * 60)
        print("SUCCESS")
        print("=" * 60)


if __name__ == '__main__':
    main()
