export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('endpoint_exception');

    $scope.table = [];

    paginationService.init('exceptions');
    $http.get('api/num_exceptions').then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        // formService.isLoading = true; ?
        $http.get('api/exception_info/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
            // formService.isLoading = false; ?
        });
    };
};