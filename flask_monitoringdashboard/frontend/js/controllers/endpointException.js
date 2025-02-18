export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('endpoint_exception');

    $scope.table = [];

    paginationService.init('exceptions');
    $http.get('api/num_exceptions/'+ endpointService.info.id).then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        $http.get('api/detailed_exception_info/' + endpointService.info.id + '/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
        });
    };
};
