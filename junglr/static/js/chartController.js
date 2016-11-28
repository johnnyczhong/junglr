//chartController.js

app.controller('chartController', function($scope, $http) {
	$scope.info = {};
	$scope.generateChart = function() {
		$http({
			method: 'POST',
			url: '/draw_chart',
			data: {
				info: $scope.info
			} //response is svg uri?
		}).then(function(response) {
			$scope.showlist();
			$scope.svg = response;
			$scope.info = {}
		}, function(error) {
			console.log(error);
		}
		});
	};
});