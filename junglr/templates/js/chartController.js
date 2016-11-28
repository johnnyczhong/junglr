//chartController.js

app.controller('chartController', function($scope, $http) {
    $scope.info = {};
    $scope.generate = function() {
        $http({
            method: 'POST',
            url: '/draw_chart',
            data: {
                info: $scope.info
            }
        }).then(function(response) {
            $scope.info = {};
            $scope.svg = response;
            console.log(response)
        }, function(error) {
            console.log(error);
        });
    }
});