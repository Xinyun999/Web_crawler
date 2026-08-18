import schedule
import time
from graph import build_graph


def run():
    print(f"\n{'='*55}")
    print("  SafetyWatch Agent")
    print("  LangGraph + RAG (ChromaDB) + SQL (SQLite) + MCP Tools")
    print(f"{'='*55}")

    graph = build_graph()
    result = graph.invoke({})

    print(f"\n{'='*55}")
    print(f"  完成！整体信号强度 : {result.get('overall_signal', 'N/A')}")
    print(f"  报告路径           : {result.get('report_path', 'N/A')}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()

    # 每周一 08:00 自动执行（取消注释启用定时任务）
    # schedule.every().monday.at("08:00").do(run)
    # print("定时任务已启动，每周一 08:00 自动运行。按 Ctrl+C 停止。")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
