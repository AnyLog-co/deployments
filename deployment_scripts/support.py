def merge_configs(default_configs:dict, updated_configs:dict)->dict:
    """
    Given 2 sets of configurations merge them into a single dictionary
    :args:
        default_configs:dict - the original (or default) configurations
        updated_configs:dict - the new (user defined configurations)
    :return:
        merged configurations of default_configs
    """
    for key in updated_configs:
        if isinstance(updated_configs[key], dict):
            """
            either YAML or JSON file, in which case we need to go section by section 
            """
            if key in default_configs:
                for param in updated_configs[key]:
                    if param in default_configs[key]:
                        default_configs[key][param]['default'] = updated_configs[key][param]
                        # default_configs[key][param]['default'] = updated_configs[param]
        else:
            for key in default_configs:
                for param in updated_configs:
                    if param in default_configs[key]:
                        default_configs[key][param]['default'] = updated_configs[param]

    return default_configs


def prep_configs(node_type:str, node_configs:dict, build:str=None, kubernetes_configs:dict={})->(dict, dict):
    """
    prepare configurations
    :args:
        node_type:str - node type
        node_configs:dict - AnyLog general configs
        build:str = AnyLog deployment version
        kubernetes_configs:dict - metadata for Kubernetes
    :return:
        node_configs, kubernetes_configs
    """
    node_configs['general']['NODE_TYPE']['default'] = node_type
    if node_configs['general']['NODE_TYPE']['enable'] is False:
        node_configs['general']['NODE_TYPE']['value'] = node_type
    if kubernetes_configs != {}:
        if build is not None:
            kubernetes_configs['image']['tag']['default'] = build
        kubernetes_configs['volume']['anylog_volume']['default'] = f'anylog-{node_type}-anylog-data'
        kubernetes_configs['volume']['blockchain_volume']['default'] = f'anylog-{node_type}-blockchain-data'
        kubernetes_configs['volume']['data_volume']['default'] = f'anylog-{node_type}-data-data'
        node_configs['database']['DB_IP']['default'] = 'postgres-svs'
        node_configs['database']['NOSQL_IP']['default'] = 'mongo-svs'

    if node_type != 'rest':
        node_configs['general']['NODE_NAME']['default'] = f'anylog-{node_type}'
    if node_type == 'operator':
        node_configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        node_configs['networking']['ANYLOG_REST_PORT']['default'] = 32149
    if node_type == 'publisher':
        node_configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        node_configs['networking']['ANYLOG_REST_PORT']['default'] = 32249
    if node_type == 'query':
        node_configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        node_configs['networking']['ANYLOG_REST_PORT']['default'] = 32349
        node_configs['database']['SYSTEM_QUERY']['default'] = 'true'
        node_configs['database']['MEMORY']['default'] = 'true'

    return node_configs, kubernetes_configs


def prep_imported_kubernetes(configs:dict)->dict:
    """
    Given Kubernetes configurations, update boolean values to match proper formatting
    for geolocation, if the value is default ("0.0, 0.0" or "Unknown") then reset to empty
    :args:
        configs:dict - AnyLog configurations from file to review
    :return:
         updated configs
    """
    for section in configs:
        for param in configs[section]:
            if isinstance(configs[section][param], bool):
                configs[section][param] = 'false'
                if configs[section][param] is True:
                    configs[section][param] = 'true'
            elif param == 'LOCATION' and configs[section][param] == '0.0, 0.0':
                configs[section][param] = ""
            elif param in ['COUNTRY', 'STATE', 'CITY'] and configs[section][param] == 'Unknown':
                configs[section][param] = ""

    return configs


def prepare_mqtt_params(configs:dict, db_name:str, port:int, user:str, password:str)->dict:
    """
    update the default MQTT parameters to match information already provided by the user.
    :args:
        configs:dict - (preset) MQTT configurations
        db_name:str - default logical database
        port:int - AnyLog broker port
        user:str - authentication user
        password:str - authentication user
    :return:
        (updated) configs
    """
    configs['MQTT_DBMS']['default'] = db_name
    # if local broker port is set, then update configs accordingly
    if port != "":
        configs['MQTT_PORT']['default'] = port
        configs['MQTT_BROKER']['default'] = 'local'
        configs['MQTT_USER']['default'] = ""
        configs['MQTT_PASSWD']['default'] = ""

        if user is not None:
            configs['MQTT_USER']['default'] = user
        if password is not None:
            configs['MQTT_PASSWD']['default'] = password

    return configs


def print_questions(configs:dict)->bool:
    """
    Whether or not to print question
    :args:
        configs:dict - configuration
    :param:
        status:bool
    :return:
        if one or more of the config params is enabled return True, else returns False
    """
    for param in configs:
        if configs[param]['enable'] is True:
            return True
    return False


def create_env_configs(configs:dict)->str:
    """
    Given configurations (dict) create content to store in .env (Docker)
    :args:
        configs:dict - configurations to convert into .env convent
    :params:
        content:str - converted configs
    :return;
        content
    """
    content = ""
    for section in configs:
        content += f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---'
        for param in configs[section]:
            comment = configs[section][param]['description'].replace('\n', '')
            if configs[section][param]['default'] != "":
                comment += f" [Default: {configs[section][param]['default']}]"

            default = str(configs[section][param]['default']).strip().replace('\n', '')
            value = str(configs[section][param]['value']).strip().replace('\n', '')

            if value == "" and default == "":
                line = f"#{param}=<{section.upper()}_{param.upper()}>"
            elif value == "" and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                line = f"#{param}=<{section.upper()}_{param.upper()}>"
            elif value == "" and default != "":
                line = f"{param}={default}"
            else:
                line = f"{param}={value}"
            content += f"\n# {comment}\n{line}"

        content += '\n\n'

    return content


def create_kubernetes_metadata(node_name:str, configs:dict)->str:
    """

    """
    content = ""
    for section in configs:
        content += f"{section}: "
        if section != 'volume':
            for param in configs[section]:
                comment = configs[section][param]['description']
                if configs[section][param]['default'] != "":
                    comment += f" [Default: {configs[section][param]['default']}]"

                default = str(configs[section][param]['default']).strip().replace('\n', '')
                value = str(configs[section][param]['value']).strip().replace('\n', '')
                line = f"{param}: %s"

                if value != '':
                    line = line % value
                elif default != '':
                    line = line % default
                else:
                    line = line % '""'
                content += f"\n  # {comment}\n  {line}"
        else:
            for sub_section in configs[section]:
                if sub_section == 'enable_volume':
                    comment = configs[section][sub_section]['description']
                    if configs[section][sub_section]['default'] != "":
                        comment += f" [Default: {configs[section][sub_section]['default']}]"
                    default = str(configs[section][sub_section]['default']).strip().replace('\n', '')
                    value = str(configs[section][sub_section]['value']).strip().replace('\n', '')

                    line = f"{sub_section}: %s"
                    if value != '':
                        line = line % value
                    elif default != '':
                        line = line % default
                    else:
                        line = line % '""'

                    content += f"\n  # {comment}\n  {line}"

                else:
                    content += f"\n  {sub_section}:"
                    for param in configs[section][sub_section]:
                        if param != 'default':
                            comment = configs[section][sub_section][param]['description']
                            if configs[section][sub_section][param]['default'] != "":
                                comment += f"[Default: {configs[section][sub_section][param]['default']}]"

                            default = configs[section][sub_section][param]['default']
                            value = configs[section][sub_section][param]['value']

                            line = f"{param}: %s"
                            if value != '':
                                line = line % value
                            elif default != '':
                                line = line % default
                            else:
                                line = line % '""'

                            content += f"\n    # {comment}\n    {line}"
        content += '\n\n'

    return content


def create_kubernetes_configs(configs:dict)->dict:
    """
    Given configurations (dict) create content to store in .yml (Kubernetes)
    :args:
        configs:dict - configurations to convert into .env convent
    :params:
        content:str - converted configs
    :return:
        content
    """

    content = ""
    for section in configs:
        content += f"\n{section.replace(' ', '_')}:"
        for param in configs[section]:
            comment = configs[section][param]['description'].replace('\n', '')
            if configs[section][param]['default'] != "":
                comment += f" [Default: {configs[section][param]['default']}]"

            default = str(configs[section][param]['default']).strip().replace('\n', '')
            value = str(configs[section][param]['value']).strip().replace('\n', '')
            line = f"{param}: %s"
            if value == '*':
                line = f'{param}: "{value}"'
            elif value != '':
                line = line % value
            elif default != '':
                line = line % default
            else:
                line = line % '""'

            content += f"\n  # {comment}\n  {line}"
        content += '\n\n'

    return content
