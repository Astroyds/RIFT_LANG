"""
RIFT Standard Library - Template Module

Simple template engine for server-side rendering.
"""

import re
from typing import Dict, Any


def create_template_module(interpreter) -> Dict[str, Any]:
    """Create the Template module for RIFT."""
    
    class Template:
        """Simple template engine."""
        
        def __init__(self, template: str):
            self.template = template
        
        def render(self, context: Dict[str, Any]) -> str:
            """Render template with context."""
            result = self.template
            
            # Replace {{ variable }}
            def replace_var(match):
                key = match.group(1).strip()
                value = self._get_nested_value(context, key)
                return str(value) if value is not None else ''
            
            result = re.sub(r'\{\{\s*(.+?)\s*\}\}', replace_var, result)
            
            # Handle {% if condition %}
            result = self._process_conditionals(result, context)
            
            # Handle {% for item in items %}
            result = self._process_loops(result, context)
            
            return result
        
        def _get_nested_value(self, obj: Any, key: str) -> Any:
            """Get nested value from object using dot notation."""
            keys = key.split('.')
            value = obj
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = getattr(value, k, None)
                
                if value is None:
                    return None
            
            return value
        
        def _process_conditionals(self, text: str, context: Dict) -> str:
            """Process {% if %} {% else %} {% endif %} blocks."""
            pattern = r'\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}'
            
            def replace_if(match):
                condition = match.group(1).strip()
                if_block = match.group(2)
                else_block = match.group(3) or ''
                
                # Evaluate condition
                try:
                    value = self._get_nested_value(context, condition)
                    if value and value != '0' and value != 'false':
                        return if_block
                    else:
                        return else_block
                except:
                    return else_block
            
            return re.sub(pattern, replace_if, text, flags=re.DOTALL)
        
        def _process_loops(self, text: str, context: Dict) -> str:
            """Process {% for item in items %} blocks."""
            pattern = r'\{%\s*for\s+(\w+)\s+in\s+(.+?)\s*%\}(.*?)\{%\s*endfor\s*%\}'
            
            def replace_loop(match):
                item_name = match.group(1).strip()
                items_key = match.group(2).strip()
                loop_block = match.group(3)
                
                items = self._get_nested_value(context, items_key)
                if not items or not isinstance(items, (list, tuple)):
                    return ''
                
                result = []
                for item in items:
                    loop_context = context.copy()
                    loop_context[item_name] = item
                    
                    # Render loop block with item context
                    rendered = loop_block
                    for key, value in loop_context.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                pattern = f'{{{{{key}.{sub_key}}}}}'
                                rendered = rendered.replace(pattern, str(sub_value))
                        
                        pattern = f'{{{{{key}}}}}'
                        rendered = rendered.replace(pattern, str(value))
                    
                    result.append(rendered)
                
                return ''.join(result)
            
            return re.sub(pattern, replace_loop, text, flags=re.DOTALL)
    
    def render_template(template: str, context: Dict[str, Any]) -> str:
        """Quick render helper."""
        return Template(template).render(context)
    
    def load_template(filepath: str) -> Template:
        """Load template from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return Template(f.read())
    
    def render_file(filepath: str, context: Dict[str, Any]) -> str:
        """Load and render template file."""
        return load_template(filepath).render(context)
    
    return {
        'Template': Template,
        'render': render_template,
        'load': load_template,
        'renderFile': render_file,
    }
