from ui_utils import ui, console
from project_data_manager import project_data_manager
from workflow_ui import handle_creative_workflow
from export_ui import handle_novel_export
from project_manager import project_manager
from rich.panel import Panel
from datetime import datetime

def show_workbench():
    """显示项目工作台菜单"""
    try:
        while True:
            console.clear()
            active_project_name = project_data_manager.get_current_project_display_name()
            title = f"工作台 (当前项目: 《{active_project_name}》)"

            # 显示项目状态
            dm = project_data_manager.get_data_manager()
            if dm:
                status_details = dm.get_project_status_details()
                ui.print_project_status(status_details)
                
            menu_options = [
                "开始 / 继续创作",
                "查看项目概览",
                "管理Canon Bible（创作规范）",
                "导出小说",
                "返回项目管理"
            ]
            
            choice = ui.display_menu(title, menu_options)

            if choice == '1':
                handle_creative_workflow() 
            elif choice == '2':
                show_project_overview()
            elif choice == '3':
                handle_canon_bible_management()
            elif choice == '4':
                handle_novel_export()
            elif choice == '0':
                break
    
    except KeyboardInterrupt:
        # 重新抛出 KeyboardInterrupt 让上层处理
        raise

def show_project_overview():
    """显示当前项目的详细概览"""
    console.clear()
    active_project_name = project_data_manager.get_current_project_display_name()
    ui.print_title(f"项目概览 - 《{active_project_name}》")
    
    # 获取项目元数据
    info = project_manager.get_project_info(project_manager.get_active_project())
    if info:
        try:
            created_at = datetime.fromisoformat(info.created_at).strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            created_at = "未知"
            
        try:
            last_accessed = datetime.fromisoformat(info.last_accessed).strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            last_accessed = "未知"

        details = f"""
[cyan]项目名称:[/cyan] {info.name}
[cyan]显示名称:[/cyan] {info.display_name}
[cyan]项目描述:[/cyan] {info.description or '无描述'}
[cyan]项目路径:[/cyan] {info.path}
[cyan]创建时间:[/cyan] {created_at}
[cyan]最后访问:[/cyan] {last_accessed}
        """.strip()
        console.print(Panel(details, title="项目元数据", border_style="cyan"))
    else:
        ui.print_warning("无法获取项目元数据。")

    # 获取项目进度
    dm = project_data_manager.get_data_manager()
    if dm:
        status_details = dm.get_project_status_details()
        ui.print_project_status(status_details)
    else:
        ui.print_warning("无法获取项目进度。")
        
    ui.pause()


def handle_canon_bible_management():
    """处理Canon Bible管理"""
    from llm_service import llm_service
    
    try:
        while True:
            console.clear()
            active_project_name = project_data_manager.get_current_project_display_name()
            title = f"Canon Bible管理 (项目: 《{active_project_name}》)"
            
            # 检查当前是否有Canon Bible
            dm = project_data_manager.get_data_manager()
            canon_data = dm.read_canon_bible()
            
            if canon_data and canon_data.get("canon_content"):
                status_text = "✅ 已设置"
                canon_content = str(canon_data.get("canon_content", ""))
                preview = canon_content[:100] + "..." if len(canon_content) > 100 else canon_content
                console.print(f"[cyan]当前Canon状态:[/cyan] {status_text}")
                console.print(f"[dim]内容预览: {preview}[/dim]\n")
            else:
                status_text = "❌ 未设置"
                console.print(f"[cyan]当前Canon状态:[/cyan] {status_text}\n")
            
            menu_options = [
                "查看Canon Bible详情",
                "生成新的Canon Bible",
                "重新生成Canon Bible",
                "删除Canon Bible",
                "返回工作台"
            ]
            
            choice = ui.display_menu(title, menu_options)
            
            if choice == '1':
                view_canon_bible_details(dm, canon_data)
            elif choice == '2':
                if canon_data and canon_data.get("canon_content"):
                    if ui.confirm("已存在Canon Bible，是否覆盖？"):
                        generate_canon_bible_interactive(dm)
                else:
                    generate_canon_bible_interactive(dm)
            elif choice == '3':
                if canon_data and canon_data.get("canon_content"):
                    generate_canon_bible_interactive(dm)
                else:
                    ui.print_warning("尚未设置Canon Bible，请先生成。")
                    ui.pause()
            elif choice == '4':
                if canon_data and canon_data.get("canon_content"):
                    if ui.confirm("确定要删除Canon Bible吗？此操作不可恢复。"):
                        dm.delete_canon_bible()
                        ui.print_success("Canon Bible已删除。")
                        ui.pause()
                else:
                    ui.print_warning("没有Canon Bible可删除。")
                    ui.pause()
            elif choice == '0':
                break
                
    except KeyboardInterrupt:
        raise


def view_canon_bible_details(dm, canon_data):
    """查看Canon Bible详情"""
    console.clear()
    
    if not canon_data or not canon_data.get("canon_content"):
        ui.print_warning("尚未设置Canon Bible。")
        ui.pause()
        return
    
    console.print(Panel("📖 Canon Bible详情", border_style="cyan"))
    
    # 显示基础信息
    console.print(f"[cyan]主题:[/cyan] {canon_data.get('one_line_theme', '未设置')}")
    console.print(f"[cyan]体裁:[/cyan] {canon_data.get('selected_genre', '未设置')}")
    console.print(f"[cyan]目标读者:[/cyan] {canon_data.get('audience_and_tone', '未设置')}")
    console.print(f"[cyan]创建时间:[/cyan] {canon_data.get('created_at', '未知')}")
    console.print(f"[cyan]更新时间:[/cyan] {canon_data.get('updated_at', '未知')}")
    
    console.print("\n[cyan]Canon内容:[/cyan]")
    console.print(Panel(canon_data.get('canon_content', ''), border_style="dim"))
    
    ui.pause()


def generate_canon_bible_interactive(dm):
    """交互式生成Canon Bible"""
    from llm_service import llm_service
    
    console.print(Panel("📖 生成Canon Bible", border_style="cyan"))
    
    # 收集信息
    one_line_theme = ui.prompt("请输入一句话小说主题")
    if not one_line_theme:
        ui.print_warning("操作已取消")
        return
        
    selected_genre = ui.prompt("请输入小说体裁（如：科幻、奇幻、悬疑、情感等）")
    if not selected_genre:
        ui.print_warning("操作已取消")
        return
        
    audience_and_tone = ui.prompt("请输入目标读者与语域偏好（可选）", default="")
    
    # 检查AI服务
    if not llm_service.is_available():
        ui.print_error("AI服务不可用，请检查配置。")
        ui.pause()
        return
    
    # 生成Canon Bible
    ui.print_info("正在生成Canon Bible，请稍候...")
    
    try:
        canon_result = llm_service.generate_canon_bible(
            one_line_theme=one_line_theme,
            selected_genre=selected_genre,
            audience_and_tone=audience_and_tone
        )
        
        if canon_result:
            # 保存
            canon_data = {
                "one_line_theme": one_line_theme,
                "selected_genre": selected_genre,
                "audience_and_tone": audience_and_tone,
                "canon_content": canon_result if isinstance(canon_result, str) else str(canon_result)
            }
            
            if dm.write_canon_bible(canon_data):
                ui.print_success("✅ Canon Bible生成并保存成功！")
                
                # 显示预览
                console.print("\n[cyan]生成的Canon Bible概览：[/cyan]")
                canon_str = str(canon_result)
                preview = canon_str[:300] + "..." if len(canon_str) > 300 else canon_str
                console.print(Panel(preview, border_style="dim"))
            else:
                ui.print_error("Canon Bible生成成功但保存失败")
        else:
            ui.print_error("Canon Bible生成失败")
            
    except Exception as e:
        ui.print_error(f"生成Canon Bible时出错: {e}")
    
    ui.pause()
