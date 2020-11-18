const printArea = document.querySelector("#doc-content");
const printBtn = document.querySelector("#doc-button");

const printDoc = () => {
  window.print();
};

printBtn.addEventListener("click", printDoc);
