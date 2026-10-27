document.addEventListener("DOMContentLoaded", () => {
    const sudokuBoard = document.getElementById("sudoku-board");
    const message = document.getElementById("message");
    const checkSolutionButton = document.getElementById("check-solution");

    const initialBoard = generateSudoku();
    renderBoard(initialBoard);

    checkSolutionButton.addEventListener("click", () => {
        const userSolution = getUserSolution();
        if (isSolutionCorrect(userSolution, initialBoard)) {
            message.textContent = "Yaaay!";
        } else {
            message.textContent = "Try again!";
        }
    });

    function generateSudoku() {
        const board = Array.from({ length: 9 }, () => Array(9).fill(0));
        fillDiagonalRegions(board);
        fillRemaining(board, 0, 3);
        removeDigits(board);
        return board;
    }

    function fillDiagonalRegions(board) {
        for (let i = 0; i < 9; i += 3) {
            fillRegion(board, i, i);
        }
    }

    function fillRegion(board, row, col) {
        const nums = shuffle(Array.from({ length: 9 }, (_, i) => i + 1));
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                board[row + i][col + j] = nums[i * 3 + j];
            }
        }
    }

    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function fillRemaining(board, row, col) {
        if (col >= 9 && row < 8) {
            row++;
            col = 0;
        }
        if (row >= 9 && col >= 9) return true;

        if (row < 3) {
            if (col < 3) col = 3;
        } else if (row < 6) {
            if (col === Math.floor(row / 3) * 3) col += 3;
        } else {
            if (col === 6) {
                row++;
                col = 0;
                if (row >= 9) return true;
            }
        }

        for (let num = 1; num <= 9; num++) {
            if (isSafe(board, row, col, num)) {
                board[row][col] = num;
                if (fillRemaining(board, row, col + 1)) return true;
                board[row][col] = 0;
            }
        }
        return false;
    }

    function isSafe(board, row, col, num) {
        return !usedInRow(board, row, num) &&
               !usedInCol(board, col, num) &&
               !usedInBox(board, row - row % 3, col - col % 3, num);
    }

    function usedInRow(board, row, num) {
        return board[row].includes(num);
    }

    function usedInCol(board, col, num) {
        return board.some(row => row[col] === num);
    }

    function usedInBox(board, boxStartRow, boxStartCol, num) {
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < 3; col++) {
                if (board[row + boxStartRow][col + boxStartCol] === num) {
                    return true;
                }
            }
        }
        return false;
    }

    function removeDigits(board) {
        let count = 30; // Number of cells to remove
        while (count !== 0) {
            const cellId = Math.floor(Math.random() * 81);
            const row = Math.floor(cellId / 9);
            const col = cellId % 9;
            if (board[row][col] !== 0) {
                board[row][col] = 0;
                count--;
            }
        }
    }

    function renderBoard(board) {
        sudokuBoard.innerHTML = ''; // Clear the board first
        board.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                const input = document.createElement("input");
                input.type = "number";
                input.min = 1;
                input.max = 9;
                if (cell !== 0) {
                    input.value = cell;
                    input.disabled = true;
                }
                input.dataset.row = rowIndex;
                input.dataset.col = colIndex;
                sudokuBoard.appendChild(input);
            });
        });
    }

    function getUserSolution() {
        const inputs = document.querySelectorAll("input[type='number']");
        const solution = Array.from({ length: 9 }, () => Array(9).fill(0));
        inputs.forEach(input => {
            const row = parseInt(input.dataset.row, 10);
            const col = parseInt(input.dataset.col, 10);
            solution[row][col] = parseInt(input.value, 10) || 0;
        });
        return solution;
    }

    function isSolutionCorrect(solution, initialBoard) {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (initialBoard[row][col] === 0 && !isValid(solution, row, col, solution[row][col])) {
                    return false;
                }
            }
        }
        return true;
    }

    function isValid(board, row, col, num) {
        return !usedInRow(board, row, num) &&
               !usedInCol(board, col, num) &&
               !usedInBox(board, row - row % 3, col - col % 3, num);
    }
});