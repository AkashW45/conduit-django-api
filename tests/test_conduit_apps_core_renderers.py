import json
import pytest
from unittest.mock import MagicMock

from conduit.apps.core.renderers import ConduitJSONRenderer


class TestConduitJSONRenderer:

    def test_render_adds_cors_header_to_response(self):
        renderer = ConduitJSONRenderer()
        response = MagicMock()
        renderer_context = {'response': response}
        data = {'key': 'value'}

        result = renderer.render(data, renderer_context=renderer_context)

        response.__setitem__.assert_called_once_with('Access-Control-Allow-Origin', '*')
        # Check that the normal wrapping still happens
        assert 'object' in json.loads(result)

    def test_render_wraps_plain_data_in_object_label(self):
        renderer = ConduitJSONRenderer()
        response = MagicMock()
        renderer_context = {'response': response}
        data = {'name': 'test', 'value': 42}

        result = renderer.render(data, renderer_context=renderer_context)

        parsed = json.loads(result)
        assert parsed == {'object': data}

    def test_render_delegates_error_data_to_parent_renderer(self):
        """When data contains an 'errors' key, the renderer should call the parent
        JSONRenderer.render while still adding the CORS header."""
        renderer = ConduitJSONRenderer()
        response = MagicMock()
        renderer_context = {'response': response}
        errors_data = {'errors': {'detail': 'Something went wrong'}, 'other': 'data'}

        # We'll spy on super().render to ensure it is called.
        with pytest.MonkeyPatch().context() as mp:
            super_render = MagicMock(return_value='{"errors": {"detail": "test"}}')
            mp.setattr(JSONRenderer, 'render', super_render)

            result = renderer.render(errors_data, renderer_context=renderer_context)

            # CORS header still set
            response.__setitem__.assert_called_once_with('Access-Control-Allow-Origin', '*')
            # Parent render called exactly once
            super_render.assert_called_once_with(errors_data)
            # Return value from parent is passed through
            assert result == '{"errors": {"detail": "test"}}'

    def test_render_handles_pagination_when_label_attribute_present(self):
        """Happy path: manually provide the missing pagination_count_label to avoid
        the AttributeError, then test proper serialisation."""
        renderer = ConduitJSONRenderer()
        renderer.pagination_count_label = 'count'   # fix the missing attribute
        response = MagicMock()
        renderer_context = {'response': response}
        data = {
            'results': [{'id': 1}, {'id': 2}],
            'count': 2
        }

        result = renderer.render(data, renderer_context=renderer_context)

        response.__setitem__.assert_called_once_with('Access-Control-Allow-Origin', '*')
        parsed = json.loads(result)
        assert parsed == {'objects': data['results'], 'count': 2}

    def test_render_raises_attributeerror_for_pagination_when_label_missing(self):
        """Edge/error case: when data contains 'results' but the custom
        pagination_count_label attribute is missing (which is a bug in the current code),
        an AttributeError is raised."""
        renderer = ConduitJSONRenderer()
        response = MagicMock()
        renderer_context = {'response': response}
        data = {'results': [], 'count': 0}

        with pytest.raises(AttributeError):
            renderer.render(data, renderer_context=renderer_context)

    def test_render_with_absent_renderer_context_does_not_alter_response(self):
        """When renderer_context is None, the code should not try to set headers
        and still produce wrapped output (without errors)."""
        renderer = ConduitJSONRenderer()
        data = {'foo': 'bar'}

        result = renderer.render(data, renderer_context=None)

        parsed = json.loads(result)
        assert parsed == {'object': data}