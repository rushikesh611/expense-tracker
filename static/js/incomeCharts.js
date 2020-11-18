let ctx = document.getElementById("myChart").getContext("2d");
let loader = document.querySelector("#loading-stuff");

const getData = async () => {
  const data = await (await fetch("/income/summary_rest")).json();
  const [labels1, values1, labels2, values2] = [
    Object.keys(data.data.months),
    Object.values(data.data.months),
    Object.keys(data.data.days),
    Object.values(data.data.days),
  ];
  const letteredLabels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
  ];
  showChart(
    letteredLabels,
    values1,
    ["Mon", "Tue", "Wed", "Thur", "Fri", "Sar", "Sun"],
    values2
  );
};

getData();

const showChart = (labels1, values1, labels2, values2) => {
  loader.style.display = "none";
  var chart = new Chart(ctx, {
    // The type of chart we want to create
    type: "line",

    // The data for our dataset
    data: {
      labels: labels1,
      datasets: [
        {
          label: "This year",
          backgroundColor: "rgb(255, 99, 132)",
          borderColor: "rgb(255, 99, 132)",
          data: values1,
        },
      ],
    },

    // Configuration options go here
    options: {},
  });

  var ctx1 = document.getElementById("myChartOne").getContext("2d");
  var chart = new Chart(ctx1, {
    // The type of chart we want to create
    type: "line",

    // The data for our dataset
    data: {
      labels: labels2,
      datasets: [
        {
          label: "This Week",
          backgroundColor: "#18BC9C",
          borderColor: "#18BC9C",
          data: values2,
        },
      ],
    },

    // Configuration options go here
    options: {},
  });
};
