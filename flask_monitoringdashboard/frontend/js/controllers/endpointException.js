export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService) {
    Prism.plugins.NormalizeWhitespace.setDefaults({
        'remove-trailing': false,
        'remove-indent': false,  
        'left-trim': true,
        'right-trim': true
    });
    endpointService.reset();
    menuService.reset('endpoint_exception');
    $scope.id2Function = {};

    $scope.table = [];

    endpointService.onNameChanged = function (name) {
        $scope.title = 'Exceptions for ' + name;
    };

    paginationService.init('exceptions');
    $http.get('api/num_exceptions/'+ endpointService.info.id).then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        $http.get('api/detailed_exception_info/' + endpointService.info.id + '/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
        });
    };

    $scope.getUniqueKey = function (function_id, stack_trace_id) {
        return `code_${function_id}_${stack_trace_id}`;
    }

    $scope.getFunctionById = function (function_id, stack_trace_id) {
        let key = $scope.getUniqueKey(function_id, stack_trace_id);
        
        if ($scope.id2Function[key] === undefined){
            $http.get(`api/function_definition/${function_id}/${stack_trace_id}`)
                .then((response) => {
                    $scope.id2Function[key] = response.data;
                    $scope.$applyAsync(() => {
                        let element = document.getElementById(key);
                        Prism.highlightElement(element);
                    });
                });
        }
    }
};
