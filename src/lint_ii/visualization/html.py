import uuid
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class LintIIVisualizer:
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_dir))

    def _repr_html_(self) -> str:
        """Render as HTML for Jupyter display"""
        try:
            visualizer_id = f"lint-ii-{uuid.uuid4()}"

            template = self.env.get_template("template.jinja.html")
            return template.render(
                visualizer_id=visualizer_id,
                data=json.dumps(self.as_dict()),
            )
        except Exception as e:
            return f"<div style='color: red;'>Error rendering LiNT-II visualizer: {e}</div>"
