from flask import jsonify

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard.controllers.exceptions import get_exception_function_definition, get_exceptions_with_timestamp, get_detailed_exception_info
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.database.exception_info import count_grouped_exceptions, count_endpoint_grouped_exceptions


@blueprint.route('/api/exception_info/<offset>/<per_page>')
@secure
def get_exception_info(offset, per_page):
    """
    Get information about all the exceptions that have occured for all endpoint
    :return: A JSON-list with a JSON-object per exception-group (grouped by endpoint and stack trace)
    """
    post_to_back_if_telemetry_enabled(**{'name': 'exception_info'}) # Ved ikke 100% hvorfor, tror det er business behov, ikke et funktionelt behov som sådan
    with session_scope() as session:
        exceptions = get_exceptions_with_timestamp(session, offset, per_page)
        
        return jsonify(exceptions)
    
@blueprint.route('/api/num_exceptions')
@secure
def num_exceptions():
    post_to_back_if_telemetry_enabled(**{'name': f'num_exceptions'})
    with session_scope() as session:
        return jsonify(count_grouped_exceptions(session))
    
@blueprint.route('/api/num_exceptions/<int:endpoint_id>')
@secure
def num_endpoint_exceptions(endpoint_id):
    post_to_back_if_telemetry_enabled(**{'name': f'num_endpoint_exceptions'})
    with session_scope() as session:
        return jsonify(count_endpoint_grouped_exceptions(session, endpoint_id))

@blueprint.route('/api/detailed_exception_info/<int:endpoint_id>/<offset>/<per_page>')
@secure
def get_detailed_exception_info_endpoint(endpoint_id, offset, per_page):
    """
    Get information about all the exceptions that have occured for a specific endpoint
    :return: A JSON-list with a JSON-object per traceback id
    """
    post_to_back_if_telemetry_enabled(**{'name': 'detailed_exception_info'})
    with session_scope() as session:
        exceptions = get_detailed_exception_info(session, offset, per_page, endpoint_id)
        
        return jsonify(exceptions)

@blueprint.route('/api/function_definition/<int:function_id>/<int:stack_trace_id>')
@secure
def get_function_definition_for_exception(function_id, stack_trace_id):
    post_to_back_if_telemetry_enabled(**{'name': 'detailed_exception_info'})
    with session_scope() as session:
        definition = get_exception_function_definition(session, function_id, stack_trace_id)
        return jsonify(definition)
