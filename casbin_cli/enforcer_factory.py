import casbin  
import os  
import tempfile  
import re  
  
class EnforcerFactory:  
    @staticmethod  
    def create_enforcer(model_input, policy_input):  
        """Create Casbin Enforcer with advanced features support"""  
        model_path = EnforcerFactory._process_input(model_input, is_model=True)  
        policy_path = EnforcerFactory._process_input(policy_input, is_model=False)  
          
        # Create enforcer  
        enforcer = casbin.Enforcer(model_path, policy_path)  
          
        # Add built-in functions for KeyMatch, RegexMatch etc.  
        EnforcerFactory._add_builtin_functions(enforcer)  
          
        # Setup role managers for multiple role definitions (g, g2, g3...)  
        EnforcerFactory._setup_role_managers(enforcer)  
          
        return enforcer  
      
    @staticmethod  
    def _add_builtin_functions(enforcer):  
        """Add built-in matching functions"""  
        # Add keyMatch function  
        def key_match(key1, key2):  
            """KeyMatch function for RESTful path matching"""  
            key2 = key2.replace('*', '.*')  
            return re.match(key2, key1) is not None  
          
        # Add keyMatch2 function  
        def key_match2(key1, key2):  
            """KeyMatch2 function for RESTful path matching with parameters"""  
            key2 = key2.replace('*', '.*')  
            key2 = re.sub(r':([^/]+)', r'[^/]+', key2)  
            return re.match(f'^{key2}$', key1) is not None  
          
        # Add keyMatch3 function  
        def key_match3(key1, key2):  
            """KeyMatch3 function for RESTful path matching"""  
            key2 = key2.replace('*', '.*')  
            key2 = re.sub(r'\{[^}]+\}', '[^/]+', key2)  
            return re.match(f'^{key2}$', key1) is not None  
          
        # Add keyMatch4 function  
        def key_match4(key1, key2):  
            """KeyMatch4 function for RESTful path matching"""  
            key2 = key2.replace('*', '.*')  
            key2 = re.sub(r'\{[^}]+\}', '[^/]+', key2)  
            return re.match(f'^{key2}$', key1) is not None  
          
        # Add keyMatch5 function  
        def key_match5(key1, key2):  
            """KeyMatch5 function for RESTful path matching"""  
            key2 = key2.replace('*', '.*')  
            key2 = re.sub(r'\{[^}]+\}', '[^/]+', key2)  
            return re.match(f'^{key2}$', key1) is not None  
          
        # Add regexMatch function  
        def regex_match(key1, key2):  
            """RegexMatch function for regular expression matching"""  
            return re.match(key2, key1) is not None  
          
        # Add ipMatch function  
        def ip_match(ip1, ip2):  
            """IPMatch function for IP address matching"""  
            import ipaddress  
            try:  
                if '/' in ip2:  
                    network = ipaddress.ip_network(ip2, strict=False)  
                    return ipaddress.ip_address(ip1) in network  
                else:  
                    return ip1 == ip2  
            except:  
                return False  
          
        # Add globMatch function  
        def glob_match(key1, key2):  
            """GlobMatch function for glob pattern matching"""  
            import fnmatch  
            return fnmatch.fnmatch(key1, key2)  
          
        # Register all functions with the enforcer  
        enforcer.add_function('keyMatch', key_match)  
        enforcer.add_function('keyMatch2', key_match2)  
        enforcer.add_function('keyMatch3', key_match3)  
        enforcer.add_function('keyMatch4', key_match4)  
        enforcer.add_function('keyMatch5', key_match5)  
        enforcer.add_function('regexMatch', regex_match)  
        enforcer.add_function('ipMatch', ip_match)  
        enforcer.add_function('globMatch', glob_match)  
      
    @staticmethod  
    def _setup_role_managers(enforcer):  
        """Setup multiple role managers for g, g2, g3..."""  
        # PyCasbin automatically handles multiple role definitions  
        # No additional setup needed for basic g, g2, g3 support  
        pass  
      
    @staticmethod  
    def _process_input(input_str, is_model=True):  
        """Processing input can be file paths or inline content"""  
        if input_str is None:  
            raise ValueError("Input cannot be null")  
          
        # Empty string policy content is allowed, but None is not  
        if input_str.strip() == "" and not is_model:  
            # For empty policy content, create a temporary file containing empty content  
            return EnforcerFactory._write_to_temp_file("")  
          
        elif input_str.strip() == "" and is_model:  
            raise ValueError("Model content cannot be empty")  
          
        # Check if it is an existing file  
        if os.path.exists(input_str) and os.path.isfile(input_str):  
            return input_str  
          
        # Verification content format  
        if is_model:  
            if not EnforcerFactory._is_valid_model_content(input_str):  
                raise ValueError("Invalid model format")  
        else:  
            if input_str.strip() and not EnforcerFactory._is_valid_policy_content(input_str):  
                raise ValueError("Invalid policy format")  
          
        # Write to a temporary file  
        return EnforcerFactory._write_to_temp_file(input_str)  
      
    @staticmethod  
    def _is_valid_model_content(content):  
        """Verify the model content format"""  
        required_sections = ['[request_definition]', '[policy_definition]',  
                           '[policy_effect]', '[matchers]']  
        return all(section in content for section in required_sections)  
      
    @staticmethod  
    def _is_valid_policy_content(content):  
        """Verify the format of the strategy content"""  
        if not content.strip():  
            return True  
        lines = content.strip().split('\n')  
        # Allow p,, g,, g2,, g3,, etc. and empty lines  
        return all(line.strip().startswith(('p,', 'g,', 'g2,', 'g3,', 'g4,')) or not line.strip()  
                  for line in lines)  
      
    @staticmethod  
    def _write_to_temp_file(content):  
        """Write the content to a temporary file"""  
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:  
            # Handle the delimiter  
            processed_content = content.replace('|', '\n')  
            f.write(processed_content)  
            f.flush()  
            return f.name