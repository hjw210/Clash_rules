import subprocess
import ipaddress


def resolve_domains(domains):
    ip_addresses = []
    dns_servers = ['8.8.8.8']
    for domain in domains:
        try:
            for dns_server in dns_servers:
                result = subprocess.run(['dig', '+short', '@' + dns_server, domain], capture_output=True, text=True)
                ips = result.stdout.strip().split('\n')
                for ip in ips:
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        if ip_obj.version == 4:
                            ip_addresses.append(ip + '/32')
                    except ValueError:
                        pass
        except subprocess.CalledProcessError as e:
            print(f"执行命令时发生错误：{e}")
        except Exception as e:
            print(f"处理域名 {domain} 时发生错误：{e}")
    return ip_addresses


def update_config_file(ip_addresses, rule_name):
    try:
        with open("config.yaml", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            existing_rules = set()
            for line in lines:
                if line.strip().startswith('- IP-CIDR,'):
                    existing_rules.add(line.strip())

        with open("config.yaml", 'a', encoding='utf-8') as file:
            for ip in ip_addresses:
                rule = f'  - IP-CIDR,{ip},{rule_name}\n'
                if rule not in existing_rules:
                    file.write(rule)
            if '  - MATCH,Proxy\n' not in existing_rules:
                file.write('  - MATCH,Proxy\n')
    except Exception as e:
        print(f"更新配置文件时发生错误：{e}")


def add_rules():
    domains_input = input("请输入要解析的域名列表，用逗号分隔：")
    rule_name = input("请输入域名规则的策略组名称：")
    domain_list = domains_input.split(',')
    ip_addresses = resolve_domains(domain_list)
    update_config_file(ip_addresses, rule_name)


if __name__ == '__main__':
    add_rules()
