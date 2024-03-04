import subprocess
import ipaddress


def add_rules():
    # 获取输入的域名列表和策略组名称
    domains_input = input("请输入要解析的域名列表，用逗号分隔：")
    rule_name = input("请输入域名规则的策略组名称：")
    # 将输入的域名列表按逗号分割成列表
    domain_list = domains_input.split(',')
    # 存储解析得到的 IP 地址
    ip_addresses = []
    dns_servers = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '9.9.9.9']
    for domain in domain_list:
        try:
            # 使用 subprocess 执行 dig 命令，指定多个 DNS 服务器，获取域名对应的 IP 地址
            dig_command = ['dig', '+short']
            for dns_server in dns_servers:
                dig_command.extend(['@' + dns_server])
            dig_command.append(domain)
            result = subprocess.run(dig_command, capture_output=True, text=True)
            ips = result.stdout.strip().split('\n')
            for ip in ips:
                # 检查 IP 地址是否为 IPv4 地址
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if ip_obj.version == 4:
                        ip_addresses.append(ip + '/32')
                except ValueError:
                    # 如果 IP 地址不是有效的 IP 地址，则跳过
                    pass
        except subprocess.CalledProcessError as e:
            print(f"执行命令时发生错误：{e}")
        except Exception as e:
            print(f"处理域名 {domain} 时发生错误：{e}")
    # 读取 config.yaml 文件内容
    with open("config.yaml", 'r', encoding='utf-8') as file:
        content = file.readlines()
        if content:
            content.pop()
        else:
            pass
    # 将修改后的内容重新写入 config.yaml 文件
    with open("config.yaml", 'w', encoding='utf-8') as file:
        file.writelines(content)
        # 将解析得到的 IP 地址写入文件
        for ip in ip_addresses:
            file.write(f'  - IP-CIDR,{ip},{rule_name}\n')
        file.write('  - MATCH,Proxy\n')


if __name__ == '__main__':
    add_rules()
