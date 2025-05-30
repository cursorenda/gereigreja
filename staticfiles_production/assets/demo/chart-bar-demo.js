document.addEventListener("DOMContentLoaded", function() {
  var ctx = document.getElementById("myBarChart").getContext("2d");
  var myBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
          labels: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"],
          datasets: [{
              label: "Receitas",
              backgroundColor: "rgba(2,117,216,1)",
              borderColor: "rgba(2,117,216,1)",
              data: [4215, 5312, 6251, 7841, 9821, 14984],
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
                  },
                  ticks: {
                      maxTicksLimit: 6
                  }
              },
              y: {
                  ticks: {
                      min: 0,
                      max: 15000,
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