import subprocess
import ipaddress
import os


def resolve_domains(domain_list):
    ip_addresses = []
    dns_servers = ['8.8.8.8']

    for domain in domain_list:
        domain = domain.strip()

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
        file_path = "config.yaml"

        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as new_file:
                new_file.write('')

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            existing_rules = set()

            for line in lines:
                if line.strip().startswith('- IP-CIDR,'):
                    existing_rules.add(line.strip())

        with open(file_path, 'a', encoding='utf-8') as file:
            for ip in ip_addresses:
                rule = f'  - IP-CIDR,{ip},{rule_name}\n'

                if rule not in existing_rules:
                    file.write(rule)

            if '  - MATCH,Proxy\n' not in existing_rules:
                file.write('  - MATCH,Proxy\n')
    except Exception as e:
        print(f"更新配置文件时发生错误：{e}")


def get_rules(rule_name, path):
    try:
        with open(path, 'r', encoding='utf-8') as domains_file:
            domain_list = domains_file.readlines()

        ip_addresses = resolve_domains(domain_list)
        update_config_file(ip_addresses, rule_name)
    except Exception as e:
        print(f"处理域名列表时发生错误：{e}")


if __name__ == '__main__':
    get_rules('ChatGPT', 'domain.txt')
