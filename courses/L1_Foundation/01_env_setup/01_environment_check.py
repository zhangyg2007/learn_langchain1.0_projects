#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 1
课程标题: 环境搭建与基础验证
学习目标: 
  - 验证Python环境配置
  - 检查和配置API密钥
  - 基础依赖包导入测试
  - 环境错误quadronnjailbreak诊断
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
"""

import sys
import os
import importlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess
from pathlib import Path

class L1EnvironmentChecker:
    """L1阶段环境检查器"""
    
    def __init__(self):
        self.checks = []
        self.issues = []
        self.recommendations = []
        
    def check_python_version(self) -> bool:
        """检查Python版本"""
        version = sys.version_info
        python_version = f"{version.major}.{version.minor}.{version.micro}"
        
        print(f"📍 Python版本检查")
        print(f"   └─ 当前版本: {python_version}")
        
        if version >= (3, 10, 0):
            print(f"   ✅ Python {python_version} ✓ (版本符合要求)")
            self.checks.append(("Python版本", "通过", python_version))
            return True
        else:
            print(f"   ❌ Python {python_version} ✗ (需要3.10+)")
            self.issues.append("Python版本过低，需要升级至3.10或更高版本")
            self.checks.append(("Python版本", "失败", python_version))
            return False

    def check_virtual_env(self) -> bool:
        """检查虚拟环境"""
        print(f"\n📍 虚拟环境检查")
        print(f"   └─ 检查是否使用虚拟环境")
        
        # 检查虚拟环境标记
        venv_methods = [
            ("VIRTUAL_ENV", os.getenv("VIRTUAL_ENV")),
            ("CONDA_DEFAULT_ENV", os.getenv("CONDA_DEFAULT_ENV")),
            ("PYENV_VIRTUAL_ENV", os.getenv("PYENV_VIRTUAL_ENV"))
        ]
        
        active_venv = None
        for env_var, value in venv_methods:
            if value:
                active_venv = (env_var, value)
                break
        
        if active_venv:
            print(f"   ✅ 检测到虚拟环境: {active_venv[1]} ({active_venv[0]}) ✓")
            self.checks.append(("虚拟环境", "通过", active_venv[1]))
            return True
        else:
            print(f"   ⚠️  未检测到虚拟环境 (建议使用)")
            self.recommendations.append("建议使用虚拟环境以避免依赖冲突")
            self.checks.append(("虚拟环境", "警告", "未使用虚拟环境"))
            return True
    
    def check_required_packages(self) -> Dict[str, str]:
        """检查必需的Python包"""
        print(f"\n📍 Python包依赖检查")
        
        required_packages = [
            ("langchain", "0.1.0", "core"),
            ("langchain_openai", "0.0.5", "openai"),
            ("langchain_core", "0.1.0", "core"),
            ("python_dotenv", "1.0.0", "utilities"),
            ("pydantic", "2.5.0", "data validation"),
            ("requests", "2.31.0", "http")
        ]
        
        package_status = {}
        
        for package_name, min_version, category in required_packages:
            print(f"   └─ 检查 {package_name} ({category})")
            
            try:
                module = importlib.import_module(package_name)
                version = getattr(module, "__version__", "unknown")
                
                # 简化版本检查
                if version != "unknown" and "." in version:
                    current = tuple(map(int, version.split(".")[:2]))
                    required = tuple(map(int, min_version.split(".")[:2]))
                    
                    if current >= required:
                        print(f"      ✅ {package_name}=={version} ✓")
                        package_status[package_name] = "通过"
                    else:
                        print(f"      ⚠️  {package_name}=={version} (建议升级至>={min_version})")
                        package_status[package_name] = "需要升级"
                else:
                    print(f"      ✅ {package_name} 已安装 ✓")
                    package_status[package_name] = "通过"
                    
            except ImportError:
                print(f"      ❌ {package_name} 未安装 ✗")
                package_status[package_name] = "缺少"
                self.issues.append(f"缺少必需依赖: {package_name}")
        
        return package_status

    def check_api_keys(self) -> Dict[str, str]:
        """检查API密钥配置"""
        print(f"\n📍 API密钥检查")
        
        # 检查.env文件是否存在
        env_file = Path(".env")
        if env_file.exists():
            print(f"   ✅ 发现.env文件 ✓")
        else:
            print(f"   ⚠️  未发现.env文件 (建议创建)")
            self.recommendations.append("建议创建.env文件并配置API密钥")

        # 检查API密钥环境变量
        required_apis = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("DEEPSEEK_API_KEY", "DeepSeek (可选)"),
            ("ZHIPU_API_KEY", "Zhipu (可选)"),
            ("MOONSHOT_API_KEY", "Moonshot (可选)")
        ]
        
        api_status = {}
        
        for api_key_name, service_name in required_apis:
            api_key = os.getenv(api_key_name)
            
            if api_key and len(api_key) > 20:
                print(f"   ✅ {service_name} API密钥已配置 ✓")
                api_status[service_name] = "已配置"
            else:
                if "可选" in service_name:
                    print(f"   📋 {service_name} - 未配置 (可选)")
                    api_status[service_name] = "未配置(可选)"
                else:
                    print(f"   ❌ {service_name} API密钥未配置 ✗")
                    api_status[service_name] = "未配置(必需)"
                    self.issues.append(f"缺少必需的API密钥: {api_key_name}")
        
        return api_status

    def check_network_connectivity(self) -> Dict[str, str]:
        """检查网络连接性"""
        print(f"\n📍 网络连接检查")
        
        # 检查基本网络连通性
        import socket
        
        hosts_to_check = [
            ("api.openai.com", 443, "OpenAI"),
            ("www.google.com", 443, "网络通用"),
        ]
        
        network_status = {}
        
        for host, port, service in hosts_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ 可连接至 {service} ({host}:{port}) ✓")
                    network_status[service] = "可连接"
                else:
                    print(f"   ❌ 无法连接至 {service} ({host}:{port}) ✗")
                    network_status[service] = "连接失败"
                    self.recommendations.append(f"请检查网络连接或代理设置 - {service}")
                    
            except Exception as e:
                print(f"   ❌ 连接测试失败: {str(e)} ✗")
                network_status[service] = f"测试错误: {str(e)}"
        
        return network_status

    def generate_status_report(self) -> str:
        """生成完整的状态报告"""
        report = f"""
🔍 LangChain L1 Foundation 环境检查报告
==========================================
检查时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 检查结果摘要:
"""
        
        # 统计结果
        total_checks = len(self.checks)
        passed_checks = len([c for c in self.checks if c[1] == "通过"])
        failed_checks = len([c for c in self.checks if c[1] == "失败"])
        warning_checks = len([c for c in self.checks if c[1] == "警告"])
        
        report += f"   ✅ 通过: {passed_checks}/{total_checks}\n"
        report += f"   ❌ 失败: {failed_checks}/{total_checks}\n"  
        report += f"   ⚠️ 警告: {warning_checks}/{total_checks}\n"
        
        if self.issues:
            report += f"\n🚨 需要解决的问题:\n"
            for issue in self.issues:
                report += f"   • {issue}\n"
        
        if self.recommendations:
            report += f"\n💡 建议和推荐:\n"
            for rec in self.recommendations:
                report += f"   • {rec}\n"
        
        report += f"\n🎯 下一步学习建议:\n"
        
        # 根据检查结果给出建议
        if failed_checks == 0 and warning_checks == 0:
            report += "   🎉 恭喜！环境准备就绪，可以开始学习Week 1课程内容\n"
            report += "   📚 推荐下一步：运行 02_chain_basics.py 学习链式编程\n"
        elif failed_checks == 0:
            report += "   ✅ 环境基本符合要求，建议处理警告信息\n"
            report += "   📚 开始基础学习的同时，逐步优化环境配置\n"
        else:
            report += "   ⚠️ 请先解决环境配置问题\n"
            report += "   🔧 参考.env.example文件配置API密钥\n"
            report += "   📋 确认所有必需依赖已正确安装\n"
        
        report += f"\n📖 相关学习资源:\n"
        report += f"   📍 L1 Foundation课程大纲: ../course_outline.md\n"
        report += f"   📍 环境配置指南: ../../setup_guide.md\n"
        report += f"   📍 API密钥获取: https://platform.openai.com/\n"
        
        return report

    def save_report(self, report: str):
        """保存检查报告"""
        report_file = "01_environment_check_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📋 详细检查报告已保存至: {report_file}")

def main():
    """主函数：执行完整的环境检查"""
    
    print("🎯 LangChain L1 Foundation - Week 1: 环境检查")
    print("=" * 60)
    print("本检查工具将验证您的学习环境的各项配置是否符合课程要求")
    
    checker = L1EnvironmentChecker()
    
    try:
        # 执行各项检查
        print("开始执行环境检查...")
        
        # 核心环境检查
        python_ok = checker.check_python_version()
        venv_ok = checker.check_virtual_env()
        packages_ok = checker.check_required_packages()
        apis_ok = checker.check_api_keys()
        network_ok = checker.check_network_connectivity()
        
        # 生成报告
        report = checker.generate_status_report()
        print(report)
        
        # 保存详细报告
        checker.save_report(report)
        
        # 最终验证
        print("\n" + "=" * 60)
        if not python_ok or "缺少" in str(packages_ok):
            print("❌ 环境检查未通过，请先解决上述问题")
            return False
        else:
            print("✅ 环境检查通过！可以开始LangChain 1.0的学习之旅")
            print("\n🚀 推荐下一步:")
            print("   1. 如尚未配置API密钥，请先完成配置")
            print("   2. 运行 02_chain_basics.py 学习链式编程基础") 
            print("   3. 开始学习 Week 1 的其他课程内容")
            return True
            
    except KeyboardInterrupt:
        print("\n\n⚠️  环境检查被用户中断")
        return False
    except Exception as e:
        print(f"\n\n❌ 环境检查过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎓 基础环境就绪，准备开始LangChain学习！")