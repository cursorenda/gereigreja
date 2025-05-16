document.addEventListener("DOMContentLoaded", function() {
  var ctx = document.getElementById("myAreaChart").getContext("2d");
  var myLineChart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho"],
          datasets: [{
              label: "Visitas",
              lineTension: 0.3,
              backgroundColor: "rgba(2,117,216,0.2)",
              borderColor: "rgba(2,117,216,1)",
              pointRadius: 5,
              pointBackgroundColor: "rgba(2,117,216,1)",
              pointBorderColor: "rgba(255,255,255,0.8)",
              pointHoverRadius: 5,
              pointHoverBackgroundColor: "rgba(2,117,216,1)",
              pointHitRadius: 50,
              pointBorderWidth: 2,
              data: [1000, 30162, 26263, 18394, 18287, 28682, 31274],
          }],
      },
      options: {
          scales: {
              x: {
                  time: {
                      unit: 'month'
                  },
                  grid: {
                      display: false
                  }
              },
              y: {
                  ticks: {
                      min: 0,
                      max: 40000,
                      maxTicksLimit: 5
                  },
                  grid: {
                      color: "rgba(0, 0, 0, .125)",
                  }
              },
          },
          plugins: {
              legend: {
                  display: false
              }
          }
      }
  });
});