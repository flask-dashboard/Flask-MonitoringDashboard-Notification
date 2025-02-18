export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService) {
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

    $scope.getFunctionById = function (function_id) {
        if ($scope.id2Function[function_id] === undefined){
            $http.get(`api/function_definition/${function_id}`)
                .then((response) => {
                    $scope.id2Function[function_id] = response.data;
                })
        }
    }
};
