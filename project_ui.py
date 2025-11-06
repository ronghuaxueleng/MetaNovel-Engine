from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from datetime import datetime
from project_manager import project_manager
from project_data_manager import project_data_manager
from ui_utils import ui, console
from workbench_ui import show_workbench
import json
import re

def fix_json_quotes(json_string):
    """
    修复JSON字符串中未转义的双引号问题
    """
    # 首先尝试正常解析
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        pass
    
    # 如果失败，尝试修复引号问题
    try:
        def fix_quotes_in_string(match):
            """修复字符串值中的双引号"""
            key = match.group(1)  # 键名
            value = match.group(2)  # 值内容
            
            # 转义值中的双引号
            escaped_value = value.replace('"', '\\"')
            
            return f'"{key}": "{escaped_value}"'
        
        # 使用正则表达式匹配 "key": "value" 模式，允许值中包含双引号
        pattern = r'"([^"]+)":\s*"([^"]*(?:"[^"]*)*)"'
        fixed_string = re.sub(pattern, fix_quotes_in_string, json_string)
        
        # 尝试解析修复后的字符串
        return json.loads(fixed_string)
        
    except (json.JSONDecodeError, re.error):
        pass
    
    return None

def handle_project_management():
    """处理项目管理的UI和逻辑"""
    try:
        while True:
            console.clear()
            
            current_project = project_manager.get_active_project()
            current_display_name = "无"
            if current_project:
                info = project_manager.get_project_info(current_project)
                current_display_name = info.display_name if info else "未知"
            
            title = f"项目管理 (当前: {current_display_name})"
            
            menu_options = [
                "选择并进入项目",
                "创建新项目",
                "管理项目列表",
                "返回主菜单"
            ]
            
            choice = ui.display_menu(title, menu_options)

            if choice == '1':
                select_and_enter_project()
            elif choice == '2':
                create_new_project()
            elif choice == '3':
                manage_project_list()
            elif choice == '0':
                break
    
    except KeyboardInterrupt:
        # 重新抛出 KeyboardInterrupt 让上层处理
        raise

def select_and_enter_project():
    """选择一个项目并进入其工作台"""
    projects = project_manager.list_projects()
    if not projects:
        ui.print_warning("暂无项目。请先创建一个新项目。")
        ui.pause()
        return

    current_project = project_manager.get_active_project()
    
    choices = []
    for p in projects:
        status = " (当前)" if p.name == current_project else ""
        choices.append(f"{p.display_name}{status}")
    choices.append("返回")

    choice_str = ui.display_menu("请选择要进入的项目:", choices)
    
    if choice_str.isdigit() and choice_str != '0':
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(projects):
            selected_project = projects[choice_index]
            project_data_manager.switch_project(selected_project.name)
            ui.print_success(f"已进入项目: 《{selected_project.display_name}》")
            show_workbench() # 进入项目工作台
    
def manage_project_list():
    """提供编辑、删除、查看详情等项目管理功能"""
    try:
        while True:
            list_all_projects() # 先展示列表
            
            menu_options = [
                "编辑项目信息",
                "删除项目",
                "查看项目详情",
                "返回"
            ]
            choice = ui.display_menu("管理项目列表", menu_options)

            if choice == '1':
                edit_project()
            elif choice == '2':
                delete_project()
            elif choice == '3':
                show_project_details()
            elif choice == '0':
                break
    
    except KeyboardInterrupt:
        # 重新抛出 KeyboardInterrupt 让上层处理
        raise

def list_all_projects():
    """列出所有项目"""
    projects = project_manager.list_projects()
    
    if not projects:
        console.print("[yellow]暂无项目。请先创建一个项目。[/yellow]")
        return
    
    # 创建表格
    table = Table(title="📚 所有项目")
    table.add_column("项目名称", style="cyan", no_wrap=True)
    table.add_column("显示名称", style="green")
    table.add_column("描述", style="white")
    table.add_column("创建时间", style="yellow")
    table.add_column("最后访问", style="magenta")
    table.add_column("状态", style="red")
    
    current_project = project_manager.get_active_project()
    
    for project in projects:
        # 格式化时间
        try:
            created_time = datetime.fromisoformat(project.created_at).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            created_time = "未知"
        
        try:
            access_time = datetime.fromisoformat(project.last_accessed).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            access_time = "未知"
        
        # 状态标识
        status = "活动" if project.name == current_project else "非活动"
        
        table.add_row(
            project.name,
            project.display_name,
            project.description or "无描述",
            created_time,
            access_time,
            status
        )
    
    console.print(table)

def create_new_project():
    """创建新项目"""
    console.print(Panel("📝 创建新项目", border_style="green"))
    
    # 输入项目名称
    project_name = ui.prompt("请输入项目名称（用作目录名）")
    
    if not project_name:
        console.print("[yellow]操作已取消[/yellow]")
        return
    
    # 输入显示名称
    display_name = ui.prompt("请输入显示名称（可选，留空则使用项目名称）", default=project_name)
    
    if display_name is None:
        console.print("[yellow]操作已取消[/yellow]")
        return
    
    # 输入项目描述
    description = ui.prompt("请输入项目描述（可选）")
    
    if description is None:
        console.print("[yellow]操作已取消[/yellow]")
        return
    
    # 创建项目
    if project_manager.create_project(project_name.strip(), display_name.strip(), description.strip()):
        console.print(f"[green]✅ 项目 '{display_name or project_name}' 创建成功！[/green]")
        
        # 询问是否切换到新项目
        if ui.confirm("是否切换到新创建的项目？", default=True):
            project_data_manager.switch_project(project_name.strip())
            ui.print_success(f"已切换到项目: 《{display_name or project_name}》")
            
            # 询问是否立即生成Canon Bible
            if ui.confirm("是否现在生成项目的Canon Bible（创作规范）？", default=True):
                # 询问生成模式
                mode_choice = ui.prompt("选择生成模式：\n1. 快速模式（仅基础信息）\n2. 详细配置模式\n请选择 (1/2)", default="1")
                detailed_mode = mode_choice == "2"
                generate_canon_bible_for_new_project(detailed_mode)
    else:
        console.print("[red]❌ 项目创建失败[/red]")

def switch_project():
    # This function is now obsolete and replaced by select_and_enter_project
    pass

def delete_project():
    """删除项目"""
    selected_project = None
    
    # Let user select which project to delete
    projects = project_manager.list_projects()
    if not projects:
        ui.print_warning("没有可删除的项目。")
        return

    choices = [p.display_name for p in projects]
    choices.append("取消")
    
    choice_str = ui.display_menu("请选择要删除的项目:", choices)

    if choice_str.isdigit() and choice_str != '0':
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(projects):
            selected_project = projects[choice_index]
        else:
            ui.print_warning("无效的选择。")
            return
    else: # User cancelled
        return
        
    if not selected_project:
        ui.print_error("未找到选中的项目。")
        return
    
    # 确认删除
    console.print(f"[red]⚠️  警告：即将删除项目 '{selected_project.display_name}'[/red]")
    console.print("[red]此操作将永久删除该项目的所有数据，无法恢复！[/red]")
    
    if ui.confirm(f"确定要删除项目 '{selected_project.display_name}' 吗？", default=False):
        if project_manager.delete_project(selected_project.name):
            console.print(f"[green]✅ 项目 '{selected_project.display_name}' 已删除[/green]")
        else:
            console.print("[red]❌ 删除项目失败[/red]")
    else:
        console.print("[yellow]操作已取消[/yellow]")
    ui.pause()

def show_project_details():
    """显示项目详情"""
    projects = project_manager.list_projects()
    if not projects:
        ui.print_warning("暂无项目。")
        ui.pause()
        return
    
    # 让用户选择要查看的项目
    choices = [p.display_name for p in projects]
    choices.append("返回")
    
    choice_str = ui.display_menu("请选择要查看详情的项目:", choices)
    
    if choice_str == "0":
        return
    
    if choice_str and choice_str.isdigit():
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(projects):
            selected_project = projects[choice_index]
            _display_project_details(selected_project)
        else:
            ui.print_warning("无效的选择。")
            ui.pause()

def _display_project_details(project_info):
    """显示指定项目的详细信息"""
    # 获取项目对应的显示名称
    project_display_name = project_info.display_name or project_info.name

    # 创建详情面板
    details = f"""
[cyan]项目名称:[/cyan] {project_info.name}
[cyan]显示名称:[/cyan] {project_display_name}
[cyan]项目描述:[/cyan] {project_info.description or '无描述'}
[cyan]项目路径:[/cyan] {project_info.path}
[cyan]创建时间:[/cyan] {project_info.created_at}
[cyan]最后访问:[/cyan] {project_info.last_accessed}
    """.strip()
    
    console.print(Panel(details, title=f"📊 项目详情 - {project_display_name}", border_style="cyan"))
    ui.pause()

def edit_project():
    """编辑项目信息"""
    selected_project = None
    
    # Let user select which project to edit
    projects = project_manager.list_projects()
    if not projects:
        ui.print_warning("没有可编辑的项目。")
        return

    choices = [p.display_name for p in projects]
    choices.append("取消")
    
    choice_str = ui.display_menu("请选择要编辑的项目:", choices)
    
    if choice_str.isdigit() and choice_str != '0':
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(projects):
            selected_project = projects[choice_index]
        else:
            ui.print_warning("无效的选择。")
            return
    else: # User cancelled
        return

    if not selected_project:
        ui.print_error("未找到选中的项目。")
        return
        
    console.print(Panel(f"📝 正在编辑项目: {selected_project.display_name}", border_style="yellow"))
    
    # 编辑显示名称
    new_display_name = ui.prompt(
        "请输入新的显示名称",
        default=selected_project.display_name
    )
    
    if new_display_name is None:
        console.print("[yellow]操作已取消[/yellow]")
        return
        
    new_description = ui.prompt("输入新的描述 (留空不修改)", default=selected_project.description or "")
    if new_description is None:
        console.print("[yellow]操作已取消[/yellow]")
        return

    # 检查是否有更改
    display_name_changed = new_display_name.strip() != selected_project.display_name
    description_changed = new_description.strip() != (selected_project.description or "")
    
    if not display_name_changed and not description_changed:
        console.print("[yellow]没有任何更改[/yellow]")
        return

    update_display_name = new_display_name.strip() if display_name_changed else None
    update_description = new_description.strip() if description_changed else None

    # 更新项目
    if project_manager.update_project_info(
        selected_project.name, 
        display_name=update_display_name,
        description=update_description
    ):
        ui.print_success(f"✅ 项目 '{update_display_name or selected_project.name}' 信息已更新")
        # 刷新数据管理器以确保显示名称立即更新
        project_data_manager.refresh_data_manager()
    else:
        ui.print_error("❌ 更新项目信息失败")
    
    ui.pause()


def generate_canon_bible_for_new_project(detailed_mode=False):
    """为新创建的项目生成Canon Bible"""
    from llm_service import llm_service
    import json
    
    mode_text = "详细配置" if detailed_mode else "快速"
    console.print(Panel(f"📖 生成Canon Bible（{mode_text}模式）", border_style="cyan"))
    
    # 收集基本信息
    one_line_theme = ui.prompt("请输入您的一句话小说主题")
    if not one_line_theme:
        ui.print_warning("操作已取消")
        return
    
    selected_genre = ui.prompt("请输入小说体裁（如：科幻、奇幻、悬疑、情感等）")
    if not selected_genre:
        ui.print_warning("操作已取消")
        return
    
    audience_and_tone = ui.prompt("请输入目标读者与语域偏好（可选）:", default="")
    
    # 详细配置模式：收集更多信息
    additional_requirements = ""
    if detailed_mode:
        console.print("\n[cyan]详细配置选项（可选，直接回车跳过）：[/cyan]")
        
        # 语调偏好
        tone_preference = ui.prompt("语调偏好（如：冷静克制/激情澎湃/幽默诙谐等）:", default="")
        
        # 视角偏好
        pov_preference = ui.prompt("视角偏好（如：第一人称/第三人称近距/全知视角等）:", default="")
        
        # 节奏偏好
        rhythm_preference = ui.prompt("节奏偏好（如：快节奏/慢热型/张弛有度等）:", default="")
        
        # 世界观设定
        world_setting = ui.prompt("世界观特殊设定（如：未来科技/魔法体系/现实主义等）:", 
                                default="", multiline=True)
        
        # 禁用元素
        avoid_elements = ui.prompt("想要避免的写作元素或陈词滥调（支持多行编辑）:", 
                                 default="", multiline=True)
        
        # 特殊要求
        special_requirements = ui.prompt("其他特殊要求或偏好（支持多行编辑）:", 
                                       default="", multiline=True)
        
        # 组合额外要求
        additional_parts = []
        if tone_preference: additional_parts.append(f"语调要求：{tone_preference}")
        if pov_preference: additional_parts.append(f"视角要求：{pov_preference}")
        if rhythm_preference: additional_parts.append(f"节奏要求：{rhythm_preference}")
        if world_setting: additional_parts.append(f"世界观要求：{world_setting}")
        if avoid_elements: additional_parts.append(f"避免元素：{avoid_elements}")
        if special_requirements: additional_parts.append(f"特殊要求：{special_requirements}")
        
        if additional_parts:
            additional_requirements = "\n\n用户详细要求：\n" + "\n".join(additional_parts)
    
    # 检查AI服务是否可用
    if not llm_service.is_available():
        ui.print_error("AI服务不可用，请检查配置。")
        ui.pause()
        return
    
    # 生成Canon Bible
    ui.print_info("正在生成Canon Bible，请稍候...")
    
    try:
        # 构建用户提示
        user_prompt = additional_requirements if detailed_mode else ""
        
        canon_result = llm_service.generate_canon_bible(
            one_line_theme=one_line_theme,
            selected_genre=selected_genre,
            audience_and_tone=audience_and_tone,
            user_prompt=user_prompt
        )
        
        if canon_result:
            # 保存Canon Bible到数据管理器
            dm = project_data_manager.get_data_manager()
            # 确保canon_content是标准JSON格式
            if isinstance(canon_result, dict):
                canon_content = json.dumps(canon_result, ensure_ascii=False, indent=2)
            elif isinstance(canon_result, str):
                # 如果是字符串，尝试解析并重新格式化
                parsed = None
                
                # 尝试1：标准JSON解析
                try:
                    parsed = json.loads(canon_result)
                except json.JSONDecodeError:
                    pass
                
                # 尝试2：Python字典格式
                if parsed is None:
                    try:
                        import ast
                        parsed = ast.literal_eval(canon_result)
                    except (ValueError, SyntaxError):
                        pass
                
                # 尝试3：修复JSON中的双引号问题
                if parsed is None:
                    try:
                        parsed = fix_json_quotes(canon_result)
                    except:
                        pass
                
                # 如果成功解析，转换为标准JSON
                if parsed is not None:
                    canon_content = json.dumps(parsed, ensure_ascii=False, indent=2)
                else:
                    # 如果都失败，直接使用原字符串
                    canon_content = canon_result
            else:
                canon_content = str(canon_result)
            
            canon_data = {
                "one_line_theme": one_line_theme,
                "selected_genre": selected_genre,
                "audience_and_tone": audience_and_tone,
                "canon_content": canon_content
            }
            
            if dm.write_canon_bible(canon_data):
                ui.print_success("✅ Canon Bible 生成并保存成功！")
                
                # 显示生成的内容概览
                console.print("\n[cyan]生成的Canon Bible概览：[/cyan]")
                canon_str = str(canon_result)
                content_preview = canon_str[:200] + "..." if len(canon_str) > 200 else canon_str
                console.print(f"[dim]{content_preview}[/dim]")
            else:
                ui.print_error("Canon Bible 生成成功但保存失败")
        else:
            ui.print_error("Canon Bible 生成失败")
            
    except Exception as e:
        ui.print_error(f"生成Canon Bible时出错: {e}")
    
    ui.pause() 
