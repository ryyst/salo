"""
Format Pydantic's JSON Schemas into more human-readable format, emulating Typescript.
"""

############## WARNING: COGNITOHAZARD ###############
#                                                   #
#          not for direct human digestion           #
#   all code produced entirely by Claude Sonnet 4   #
#                                                   #
#####################################################

from typing import Dict, Any


def format_schema(runner_name: str, schema: Dict[str, Any]) -> str:
    """Transform JSON Schema into a simple human-readable format"""
    return _json_schema_to_simple_format(runner_name, schema)


def _json_schema_to_simple_format(name: str, schema: Dict[str, Any]) -> str:
    """Transform a JSON Schema into a TypeScript-like interface format with full recursive typing"""
    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))
    definitions = schema.get("$defs", {})  # Pydantic v2 uses $defs

    # Calculate global comment column position
    global_comment_column = 60  # Fixed reasonable position for all comments

    def resolve_ref(ref: str) -> Dict[str, Any]:
        """Resolve a $ref to its actual schema definition"""
        if ref.startswith("#/$defs/"):
            def_name = ref.split("/")[-1]
            return definitions.get(def_name, {})
        return {}

    def colorize(text: str, color: str) -> str:
        """Add ANSI color codes for terminal output"""
        colors = {
            "blue": "\033[94m",  # Field names
            "green": "\033[92m",  # Types
            "gray": "\033[90m",  # Comments
            "yellow": "\033[93m",  # Optional marker
            "reset": "\033[0m",
        }
        return f"{colors.get(color, '')}{text}{colors['reset']}"

    def get_field_comment(field_schema: Dict[str, Any]) -> str:
        """Extract comment from field schema (description, title, etc.)"""
        description = field_schema.get("description", "")
        if description:
            # Clean up the description and make it brief
            description = description.strip().replace("\n", " ")
            if len(description) > 50:  # Shorter for better alignment
                description = description[:47] + "..."
            return description
        return ""

    def format_comment_at_column(line_without_comment: str, comment: str) -> str:
        """Add comment at the global comment column position"""
        if not comment:
            return line_without_comment

        # Remove ANSI codes to calculate actual line length
        import re

        plain_line = re.sub(r"\033\[[0-9;]*m", "", line_without_comment)
        current_length = len(plain_line)

        if current_length < global_comment_column:
            padding = " " * (global_comment_column - current_length)
            return f"{line_without_comment}{padding}{colorize(f'// {comment}', 'gray')}"
        else:
            return f"{line_without_comment}  {colorize(f'// {comment}', 'gray')}"

    def schema_type_to_simple(
        field_schema: Dict[str, Any], max_depth: int = 5, indent: int = 2
    ) -> str:
        """Convert JSON Schema field type to simple readable type with recursion limit"""

        if max_depth <= 0:
            return "any"  # Prevent infinite recursion

        # Handle $ref (schema references)
        if "$ref" in field_schema:
            ref = field_schema["$ref"]
            resolved_schema = resolve_ref(ref)
            if resolved_schema:
                return schema_type_to_simple(resolved_schema, max_depth - 1, indent)
            else:
                # Return the ref name if we can't resolve it
                return ref.split("/")[-1]

        # Handle direct type definitions
        if "type" in field_schema:
            json_type = field_schema["type"]

            if json_type == "array":
                # Check for tuple type (prefixItems)
                prefix_items = field_schema.get("prefixItems")
                if prefix_items:
                    # This is a tuple type - show the specific types
                    tuple_types = []
                    for item_schema in prefix_items:
                        item_type = schema_type_to_simple(item_schema, max_depth - 1, indent)
                        tuple_types.append(item_type)
                    return f"[{', '.join(tuple_types)}]"

                # Regular array type
                items = field_schema.get("items", {})
                if not items:
                    return f"{colorize('Array', 'green')}<any>"

                # Handle array of arrays recursively
                item_type = schema_type_to_simple(items, max_depth - 1, indent)
                return f"{colorize('Array', 'green')}<{item_type}>"

            elif json_type == "object":
                # Check if it has defined properties (nested object)
                obj_props = field_schema.get("properties", {})
                if obj_props:
                    # Show nested object structure recursively
                    nested_fields = []
                    obj_required = set(field_schema.get("required", []))

                    for prop_name, prop_schema in obj_props.items():
                        prop_type = schema_type_to_simple(prop_schema, max_depth - 1, indent + 2)
                        opt = "?" if prop_name not in obj_required else ""
                        comment = get_field_comment(prop_schema)
                        nested_fields.append((prop_name, opt, prop_type, comment))

                    # Always format objects on multiple lines with simple formatting
                    base_indent = ""  # Closing brace gets no extra indent (will be added by caller)
                    nested_indent = "  "  # Nested content gets 2 extra spaces (will be added to caller's indent)

                    formatted_fields = []
                    for prop_name, opt, prop_type, comment in nested_fields:
                        field_part = f"{colorize(prop_name, 'blue')}{colorize(opt, 'yellow')}:"
                        # Only colorize if it doesn't already have colors
                        if "\033[" in prop_type:
                            type_part = prop_type
                        else:
                            type_part = colorize(prop_type, "green")

                        # Simple nested format: field: type
                        line_without_comment = f"{nested_indent}{field_part} {type_part}"
                        line = format_comment_at_column(line_without_comment, comment)
                        formatted_fields.append(line)

                    return "{\n" + "\n".join(formatted_fields) + f"\n{base_indent}}}"
                else:
                    return colorize("object", "green")

            # Color basic primitive types
            if json_type in ["string", "integer", "number", "boolean", "null"]:
                return colorize(json_type, "green")
            return json_type

        # Handle union types (anyOf, oneOf) recursively
        if "anyOf" in field_schema:
            types = [schema_type_to_simple(t, max_depth - 1, indent) for t in field_schema["anyOf"]]
            return f" {colorize('|', 'green')} ".join(types)

        if "oneOf" in field_schema:
            types = [schema_type_to_simple(t, max_depth - 1, indent) for t in field_schema["oneOf"]]
            return f" {colorize('|', 'green')} ".join(types)

        # Handle allOf (intersection types) recursively
        if "allOf" in field_schema:
            # For allOf, try to merge the types meaningfully
            types = []
            for subschema in field_schema["allOf"]:
                subtype = schema_type_to_simple(subschema, max_depth - 1, indent)
                if subtype != "any":
                    types.append(subtype)

            if len(types) == 1:
                return types[0]
            elif len(types) > 1:
                return " & ".join(types)  # Intersection type
            else:
                return "any"

        # Handle const values
        if "const" in field_schema:
            const_val = field_schema["const"]
            if isinstance(const_val, str):
                return f'"{const_val}"'
            else:
                return str(const_val)

        # Handle enum values
        if "enum" in field_schema:
            enum_values = field_schema["enum"]
            formatted_values = []
            for val in enum_values:
                if isinstance(val, str):
                    formatted_values.append(f'"{val}"')
                else:
                    formatted_values.append(str(val))
            return " | ".join(formatted_values)

        return "any"

    # Collect all fields with their components for tabular formatting
    fields = []
    for field_name in sorted(properties.keys()):
        field_schema = properties[field_name]
        field_type = schema_type_to_simple(field_schema)
        optional = "?" if field_name not in required_fields else ""
        comment = get_field_comment(field_schema)
        fields.append((field_name, optional, field_type, comment))

    # Format the header with optional class description
    class_description = schema.get("description", "").strip()

    desc = ": " + class_description if class_description else ""
    header_line = f"Runner {colorize(name, 'blue')}{desc}"

    lines = [header_line, "\nExpected config file format:", "{"]

    # Format each field simply - no complex padding, just comment alignment
    for field_name, optional, field_type, comment in fields:
        field_part = f"{colorize(field_name, 'blue')}{colorize(optional, 'yellow')}:"
        # Only colorize if it doesn't already have colors
        if "\033[" in field_type:
            type_part = field_type
        else:
            type_part = colorize(field_type, "green")

        # Handle object types - put comment on same line as opening brace
        if field_type.startswith("{") and comment:
            # Split at the first newline to get the opening brace line
            type_lines = field_type.split("\n")
            first_line = type_lines[0]  # This should be just "{"
            rest_lines = type_lines[1:] if len(type_lines) > 1 else []

            # Put comment after the opening brace (don't color the brace)
            colored_first_line = first_line
            line_without_comment = f"  {field_part} {colored_first_line}"
            first_line_with_comment = format_comment_at_column(line_without_comment, comment)
            lines.append(first_line_with_comment)

            # Add the remaining lines without repeating the comment
            for rest_line in rest_lines:
                lines.append(f"  {rest_line}")
        else:
            # Simple format: field: type
            line_without_comment = f"  {field_part} {type_part}"
            line = format_comment_at_column(line_without_comment, comment)
            lines.append(line)

    lines.append("}")
    return "\n".join(lines)
