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
                "生成新的Canon Bible（快速模式）",
                "生成新的Canon Bible（详细配置）",
                "编辑现有Canon Bible",
                "重新生成Canon Bible",
                "删除Canon Bible",
                "返回工作台"
            ]
            
            choice = ui.display_menu(title, menu_options)
            
            if choice == '1':
                view_canon_bible_details(dm, canon_data)
            elif choice == '2':
                # 快速模式
                if canon_data and canon_data.get("canon_content"):
                    if ui.confirm("已存在Canon Bible，是否覆盖？"):
                        generate_canon_bible_interactive(dm, detailed_mode=False)
                else:
                    generate_canon_bible_interactive(dm, detailed_mode=False)
            elif choice == '3':
                # 详细配置模式
                if canon_data and canon_data.get("canon_content"):
                    if ui.confirm("已存在Canon Bible，是否覆盖？"):
                        generate_canon_bible_interactive(dm, detailed_mode=True)
                else:
                    generate_canon_bible_interactive(dm, detailed_mode=True)
            elif choice == '4':
                # 编辑现有Canon
                if canon_data and canon_data.get("canon_content"):
                    edit_canon_bible_interactive(dm, canon_data)
                else:
                    ui.print_warning("尚未设置Canon Bible，请先生成。")
                    ui.pause()
            elif choice == '5':
                # 重新生成
                if canon_data and canon_data.get("canon_content"):
                    generate_canon_bible_interactive(dm, detailed_mode=False)
                else:
                    ui.print_warning("尚未设置Canon Bible，请先生成。")
                    ui.pause()
            elif choice == '6':
                # 删除
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


def generate_canon_bible_interactive(dm, detailed_mode=False):
    """交互式生成Canon Bible"""
    from llm_service import llm_service
    
    mode_text = "详细配置" if detailed_mode else "快速"
    console.print(Panel(f"📖 生成Canon Bible（{mode_text}模式）", border_style="cyan"))
    
    # 收集基础信息
    one_line_theme = ui.prompt("请输入一句话小说主题")
    if not one_line_theme:
        ui.print_warning("操作已取消")
        return
        
    selected_genre = ui.prompt("请输入小说体裁（如：科幻、奇幻、悬疑、情感等）")
    if not selected_genre:
        ui.print_warning("操作已取消")
        return
        
    audience_and_tone = ui.prompt("请输入目标读者与语域偏好（可选）", default="")
    
    # 详细配置模式：收集更多信息
    additional_requirements = ""
    if detailed_mode:
        console.print("\n[cyan]详细配置选项（可选，直接回车跳过）：[/cyan]")
        
        # 语调偏好
        tone_preference = ui.prompt("语调偏好（如：冷静克制/激情澎湃/幽默诙谐等）", default="")
        
        # 视角偏好
        pov_preference = ui.prompt("视角偏好（如：第一人称/第三人称近距/全知视角等）", default="")
        
        # 节奏偏好
        rhythm_preference = ui.prompt("节奏偏好（如：快节奏/慢热型/张弛有度等）", default="")
        
        # 世界观设定
        world_setting = ui.prompt("世界观特殊设定（如：未来科技/魔法体系/现实主义等）", default="")
        
        # 禁用元素
        avoid_elements = ui.prompt("想要避免的写作元素或陈词滥调", default="")
        
        # 特殊要求
        special_requirements = ui.prompt("其他特殊要求或偏好", default="")
        
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
    
    # 检查AI服务
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


def edit_canon_bible_interactive(dm, canon_data):
    """交互式编辑Canon Bible"""
    import json
    from datetime import datetime
    
    console.print(Panel("✏️ 编辑Canon Bible", border_style="yellow"))
    
    try:
        # 解析当前Canon内容
        current_canon = json.loads(canon_data.get("canon_content", "{}"))
    except json.JSONDecodeError:
        ui.print_error("Canon内容格式错误，无法编辑。")
        ui.pause()
        return
    
    while True:
        console.clear()
        console.print(Panel("✏️ 编辑Canon Bible", border_style="yellow"))
        
        # 显示当前基础信息
        console.print(f"[cyan]当前主题：[/cyan]{canon_data.get('one_line_theme', '未设置')}")
        console.print(f"[cyan]当前体裁：[/cyan]{canon_data.get('selected_genre', '未设置')}")
        console.print(f"[cyan]目标读者：[/cyan]{canon_data.get('audience_and_tone', '未设置')}")
        
        # 显示可编辑的Canon部分
        console.print("\n[cyan]可编辑的Canon部分：[/cyan]")
        editable_sections = []
        
        if 'tone' in current_canon:
            editable_sections.append("语调设定 (tone)")
        if 'pov_rules' in current_canon:
            editable_sections.append("视角规则 (pov_rules)")
        if 'theme' in current_canon:
            editable_sections.append("主题论证 (theme)")
        if 'world' in current_canon:
            editable_sections.append("世界设定 (world)")
        if 'style_do' in current_canon:
            editable_sections.append("推荐风格 (style_do)")
        if 'style_dont' in current_canon:
            editable_sections.append("禁用风格 (style_dont)")
        if 'lexicon' in current_canon:
            editable_sections.append("词汇规范 (lexicon)")
        
        menu_options = [f"编辑{section}" for section in editable_sections]
        menu_options.extend([
            "修改基础信息（主题/体裁/读者）",
            "预览完整Canon",
            "保存修改",
            "取消编辑"
        ])
        
        choice = ui.display_menu("请选择要编辑的部分", menu_options)
        
        choice_int = int(choice) if choice.isdigit() else 0
        
        if 1 <= choice_int <= len(editable_sections):
            # 编辑具体Canon部分
            section_name = editable_sections[choice_int - 1]
            edit_canon_section(current_canon, section_name)
        elif choice_int == len(editable_sections) + 1:
            # 修改基础信息
            edit_basic_info(canon_data)
        elif choice_int == len(editable_sections) + 2:
            # 预览完整Canon
            preview_canon(current_canon)
        elif choice_int == len(editable_sections) + 3:
            # 保存修改
            if save_edited_canon(dm, canon_data, current_canon):
                ui.print_success("Canon Bible修改已保存！")
                ui.pause()
                break
        elif choice_int == 0 or choice_int == len(editable_sections) + 4:
            # 取消编辑
            if ui.confirm("确定要取消编辑吗？未保存的修改将丢失。"):
                break


def edit_canon_section(current_canon, section_name):
    """编辑Canon的具体部分"""
    import json
    
    section_key = section_name.split('(')[1].rstrip(')')
    
    if section_key not in current_canon:
        ui.print_error(f"找不到部分：{section_key}")
        ui.pause()
        return
    
    console.print(f"\n[cyan]当前{section_name}内容：[/cyan]")
    current_content = json.dumps(current_canon[section_key], ensure_ascii=False, indent=2)
    console.print(Panel(current_content, border_style="dim"))
    
    console.print(f"\n[yellow]提示：您可以直接修改JSON内容，或描述您想要的修改[/yellow]")
    
    edit_choice = ui.prompt("选择编辑方式：\n1. 直接编辑JSON\n2. 描述修改要求\n请选择 (1/2)", default="2")
    
    if edit_choice == "1":
        # 直接编辑JSON
        console.print("\n请输入新的JSON内容（输入'cancel'取消）：")
        new_content = ui.prompt("", default=current_content)
        
        if new_content and new_content.lower() != 'cancel':
            try:
                new_data = json.loads(new_content)
                current_canon[section_key] = new_data
                ui.print_success(f"{section_name}已更新！")
            except json.JSONDecodeError:
                ui.print_error("JSON格式错误，修改未保存。")
    else:
        # 描述修改要求
        modification = ui.prompt(f"请描述您希望对{section_name}做什么修改")
        if modification:
            ui.print_info("注意：描述式修改需要手动实现，当前版本暂不支持AI自动修改。")
            ui.print_info(f"您的修改要求：{modification}")
    
    ui.pause()


def edit_basic_info(canon_data):
    """编辑基础信息"""
    console.print("\n[cyan]修改基础信息：[/cyan]")
    
    new_theme = ui.prompt("新的主题", default=canon_data.get('one_line_theme', ''))
    new_genre = ui.prompt("新的体裁", default=canon_data.get('selected_genre', ''))
    new_audience = ui.prompt("新的目标读者", default=canon_data.get('audience_and_tone', ''))
    
    if new_theme: canon_data['one_line_theme'] = new_theme
    if new_genre: canon_data['selected_genre'] = new_genre
    if new_audience: canon_data['audience_and_tone'] = new_audience
    
    ui.print_success("基础信息已更新！")
    ui.pause()


def preview_canon(current_canon):
    """预览完整Canon"""
    import json
    
    console.clear()
    console.print(Panel("📖 Canon Bible完整预览", border_style="cyan"))
    
    canon_str = json.dumps(current_canon, ensure_ascii=False, indent=2)
    console.print(Panel(canon_str, border_style="dim"))
    
    ui.pause()


def save_edited_canon(dm, canon_data, current_canon):
    """保存编辑后的Canon"""
    import json
    from datetime import datetime
    
    try:
        # 更新canon内容
        canon_data['canon_content'] = json.dumps(current_canon, ensure_ascii=False, indent=2)
        canon_data['updated_at'] = datetime.now().isoformat()
        
        # 保存到数据管理器
        return dm.write_canon_bible(canon_data)
    except Exception as e:
        ui.print_error(f"保存失败：{e}")
        return False
