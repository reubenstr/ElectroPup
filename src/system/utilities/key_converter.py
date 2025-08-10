class KeyConverter:
    @staticmethod
    def _snake_to_camel(snake_str: str) -> str:
        """Convert snake_case to camelCase, removing leading underscores."""
        # Remove all leading underscores
        stripped_str = snake_str.lstrip('_')
        
        if "_" not in stripped_str:            
            return stripped_str
        
        parts = stripped_str.split("_")
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    @staticmethod
    def convert_keys_to_camel_case(obj): 
        """Recursively convert dict keys from snake_case to camelCase"""
        if isinstance(obj, dict):
            return {
                KeyConverter._snake_to_camel(k): KeyConverter.convert_keys_to_camel_case(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [KeyConverter.convert_keys_to_camel_case(i) for i in obj]
        else:
            return obj
