(() => {
    const getEl = (id) => document.getElementById(id);

    const els = {
        itiId: getEl("scanner-iti-id"),
        subjectId: getEl("scanner-subject-id"),
        login: getEl("scanner-user-login"),
        password: getEl("scanner-user-password"),
        mode: getEl("scanner-mode"),
        maxFrames: getEl("scanner-max-frames"),
        subjectLoad: getEl("scanner-subject-load"),
        subjectName: getEl("scanner-subject-name"),
        start: getEl("scanner-start"),
        stop: getEl("scanner-stop"),
        torch: getEl("scanner-torch"),
        status: getEl("scanner-status"),
        video: getEl("scanner-video"),
        barcodePanel: getEl("scanner-barcode-panel"),
        resultPanel: getEl("scanner-result-panel"),
        barcodeStudentId: getEl("barcode-student-id"),
        barcodeName1: getEl("barcode-student-name1"),
        barcodeName2: getEl("barcode-student-name2"),
        barcodeClass: getEl("barcode-student-class"),
        barcodeCodes: [
            getEl("barcode-code-1"),
            getEl("barcode-code-2"),
            getEl("barcode-code-3"),
            getEl("barcode-code-4"),
            getEl("barcode-code-5"),
        ],
        barcodeFetchStudent: getEl("barcode-fetch-student"),
        barcodeSave: getEl("barcode-save"),
        barcodeClear: getEl("barcode-clear"),
        resultCode: getEl("result-code"),
        resultScore: getEl("result-score"),
        resultSave: getEl("result-save"),
        resultClear: getEl("result-clear"),
    };

    const state = {
        scanning: false,
        detector: null,
        reader: null,
        stream: null,
        track: null,
        torchOn: false,
        ean8Counts: new Map(),
        ean13Counts: new Map(),
        updateCount: 0,
        lastScan: 0,
        scanLoopId: null,
    };

    const storageKey = "itiScannerSettings";

    const setStatus = (text, isError = false) => {
        els.status.textContent = text;
        els.status.style.color = isError ? "#a62727" : "#2f3b4e";
        els.status.style.background = isError ? "#ffe6e6" : "#f0f4fa";
    };

    const loadSettings = () => {
        const raw = localStorage.getItem(storageKey);
        if (!raw) return;
        try {
            const settings = JSON.parse(raw);
            if (settings.itiId) els.itiId.value = settings.itiId;
            if (settings.subjectId) els.subjectId.value = settings.subjectId;
            if (settings.login) els.login.value = settings.login;
            if (settings.password) els.password.value = settings.password;
            if (settings.mode) els.mode.value = settings.mode;
            if (settings.maxFrames) els.maxFrames.value = settings.maxFrames;
        } catch (err) {
            console.warn("Scanner settings parse error", err);
        }
    };

    const saveSettings = () => {
        const settings = {
            itiId: els.itiId.value,
            subjectId: els.subjectId.value,
            login: els.login.value,
            password: els.password.value,
            mode: els.mode.value,
            maxFrames: els.maxFrames.value,
        };
        localStorage.setItem(storageKey, JSON.stringify(settings));
    };

    const getSettings = () => ({
        itiId: (els.itiId.value || "").trim(),
        subjectId: (els.subjectId.value || "").trim(),
        login: (els.login.value || "").trim(),
        password: els.password.value || "",
        mode: els.mode.value,
        maxFrames: Math.max(5, parseInt(els.maxFrames.value || "30", 10)),
    });

    const resetCounts = () => {
        state.ean8Counts.clear();
        state.ean13Counts.clear();
        state.updateCount = 0;
    };

    const normalizeDigits = (value) => {
        if (!value) return "";
        return String(value).replace(/\D/g, "");
    };

    const updateCountMap = (map, code) => {
        if (!code) return;
        map.set(code, (map.get(code) || 0) + 1);
    };

    const addBarcode = (format, rawValue) => {
        const digits = normalizeDigits(rawValue);
        if (!digits) return;
        const normalizedFormat = String(format || "").toLowerCase();
        if (normalizedFormat.includes("ean_8") || normalizedFormat.includes("ean8")) {
            const val = parseInt(digits, 10);
            if (Number.isNaN(val)) return;
            const studentId = Math.floor(val / 10);
            updateCountMap(state.ean8Counts, studentId);
        }
        if (normalizedFormat.includes("ean_13") || normalizedFormat.includes("ean13")) {
            const val = parseInt(digits, 10);
            if (Number.isNaN(val)) return;
            updateCountMap(state.ean13Counts, val);
        }
    };

    const getTopCode = (map) => {
        let best = null;
        let bestCount = 0;
        for (const [code, count] of map.entries()) {
            if (count > bestCount) {
                best = code;
                bestCount = count;
            }
        }
        return best;
    };

    const getStableEan13 = () => {
        if (state.updateCount === 0) return [];
        const threshold = Math.max(1, Math.floor(state.updateCount / 3));
        const items = [];
        for (const [code, count] of state.ean13Counts.entries()) {
            if (count > threshold) items.push({ code, count });
        }
        items.sort((a, b) => b.count - a.count);
        return items.map((item) => item.code);
    };

    const fillBarcodeFields = async () => {
        const studentId = getTopCode(state.ean8Counts);
        if (studentId) els.barcodeStudentId.value = studentId;
        const codes = getStableEan13();
        els.barcodeCodes.forEach((input, index) => {
            input.value = codes[index] || "";
        });
        if (studentId) {
            await fetchStudentInfo(studentId);
        }
    };

    const fillResultFields = () => {
        const bestCode = getTopCode(state.ean13Counts);
        if (bestCode) els.resultCode.value = bestCode;
    };

    const updateModeView = () => {
        const { mode } = getSettings();
        const isBarcode = mode === "barcode";
        els.barcodePanel.style.display = isBarcode ? "flex" : "none";
        els.resultPanel.style.display = isBarcode ? "none" : "flex";
        els.subjectId.disabled = isBarcode;
        els.subjectLoad.disabled = isBarcode;
    };

    const postJson = async (url, data) => {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return response.json();
    };

    const fetchSubjectInfo = async () => {
        const { itiId, subjectId, login, password } = getSettings();
        if (!itiId || !subjectId || !login || !password) {
            els.subjectName.textContent = "Заполните ИТИ, предмет и логин.";
            return;
        }
        try {
            const data = await postJson(`/${itiId}/subject_info`, {
                subject_id: subjectId,
                user_login: login,
                user_password: password,
            });
            if (data.status === "OK") {
                els.subjectName.textContent = data.subject.name;
                setStatus("Данные предмета обновлены.");
            } else {
                els.subjectName.textContent = "Предмет не найден.";
                setStatus(`Ошибка: ${data.msg || "нет доступа"}`, true);
            }
        } catch (err) {
            setStatus("Не удалось получить предмет.", true);
        }
    };

    const fetchStudentInfo = async (studentId) => {
        const { itiId, login, password } = getSettings();
        if (!itiId || !login || !password) {
            setStatus("Заполните ИТИ и логин.", true);
            return;
        }
        try {
            const data = await postJson(`/${itiId}/student_info`, {
                student_id: studentId,
                user_login: login,
                user_password: password,
            });
            if (data.status === "OK") {
                els.barcodeName1.value = data.student.name_1 || "";
                els.barcodeName2.value = data.student.name_2 || "";
                els.barcodeClass.value = `${data.student_class.class_number}${data.student_class.class_latter}`;
            } else {
                setStatus(`Ошибка: ${data.msg || "нет доступа"}`, true);
            }
        } catch (err) {
            setStatus("Не удалось получить ученика.", true);
        }
    };

    const saveBarcodes = async () => {
        const { itiId, login, password } = getSettings();
        const studentId = (els.barcodeStudentId.value || "").trim();
        if (!itiId || !login || !password || !studentId) {
            setStatus("Заполните ИТИ, логин и код школьника.", true);
            return;
        }
        const codes = els.barcodeCodes
            .map((input) => (input.value || "").trim())
            .filter((value) => value.length > 0)
            .map((value) => parseInt(value, 10))
            .filter((value) => !Number.isNaN(value));
        const payload = [[parseInt(studentId, 10), ...codes]];
        try {
            const data = await postJson(`/${itiId}/save_barcodes`, {
                data: JSON.stringify(payload),
                user_login: login,
                user_password: password,
            });
            if (data.status === "OK") {
                setStatus("Штрих-коды сохранены.");
            } else {
                setStatus(`Ошибка: ${data.msg || "не удалось сохранить"}`, true);
            }
        } catch (err) {
            setStatus("Не удалось сохранить штрих-коды.", true);
        }
    };

    const saveResult = async () => {
        const { itiId, subjectId, login, password } = getSettings();
        const code = (els.resultCode.value || "").trim();
        const result = (els.resultScore.value || "").trim();
        if (!itiId || !subjectId || !login || !password || !code || !result) {
            setStatus("Заполните ИТИ, предмет, логин, код и результат.", true);
            return;
        }
        const payload = [[code, result.replace(",", ".")]];
        try {
            const data = await postJson(`/${itiId}/${subjectId}/save_results`, {
                data: JSON.stringify(payload),
                user_login: login,
                user_password: password,
            });
            if (data.status === "OK") {
                setStatus("Результат сохранен.");
            } else {
                setStatus(`Ошибка: ${data.msg || "не удалось сохранить"}`, true);
            }
        } catch (err) {
            setStatus("Не удалось сохранить результат.", true);
        }
    };

    const stopStream = () => {
        if (state.reader) {
            state.reader.reset();
            state.reader = null;
        }
        if (state.stream) {
            state.stream.getTracks().forEach((track) => track.stop());
            state.stream = null;
            state.track = null;
        }
        state.detector = null;
        state.torchOn = false;
        els.torch.disabled = true;
    };

    const stopScan = async (auto = false) => {
        if (!state.scanning) return;
        state.scanning = false;
        if (state.scanLoopId) cancelAnimationFrame(state.scanLoopId);
        stopStream();
        els.start.disabled = false;
        els.stop.disabled = true;
        if (auto) setStatus("Сканирование завершено.");
        const { mode } = getSettings();
        if (mode === "barcode") await fillBarcodeFields();
        else fillResultFields();
    };

    const setupTorch = () => {
        if (!state.track) return;
        const capabilities = state.track.getCapabilities ? state.track.getCapabilities() : null;
        if (!capabilities || !capabilities.torch) {
            els.torch.disabled = true;
            return;
        }
        els.torch.disabled = false;
    };

    const toggleTorch = async () => {
        if (!state.track) return;
        try {
            state.torchOn = !state.torchOn;
            await state.track.applyConstraints({ advanced: [{ torch: state.torchOn }] });
        } catch (err) {
            setStatus("Подсветка не поддерживается.", true);
        }
    };

    const scanLoop = async () => {
        if (!state.scanning || !state.detector) return;
        state.updateCount += 1;
        const now = performance.now();
        if (now - state.lastScan > 150) {
            state.lastScan = now;
            try {
                const codes = await state.detector.detect(els.video);
                for (const code of codes) {
                    addBarcode(code.format, code.rawValue);
                }
            } catch (err) {
                console.warn("Detector error", err);
            }
        }
        const { maxFrames } = getSettings();
        if (state.updateCount >= maxFrames) {
            await stopScan(true);
            return;
        }
        state.scanLoopId = requestAnimationFrame(scanLoop);
    };

    const startScan = async () => {
        if (state.scanning) return;
        resetCounts();
        setStatus("Запуск камеры...");
        els.start.disabled = true;
        els.stop.disabled = false;
        state.scanning = true;
        const constraints = {
            video: {
                facingMode: { ideal: "environment" },
                width: { ideal: 1280 },
                height: { ideal: 720 },
                frameRate: { ideal: 30, max: 60 },
                advanced: [{ focusMode: "continuous" }],
            },
            audio: false,
        };

        try {
            if ("BarcodeDetector" in window) {
                state.stream = await navigator.mediaDevices.getUserMedia(constraints);
                els.video.srcObject = state.stream;
                state.track = state.stream.getVideoTracks()[0];
                await els.video.play();
                state.detector = new BarcodeDetector({ formats: ["ean_13", "ean_8"] });
                setupTorch();
                setStatus("Сканирование запущено.");
                scanLoop();
                return;
            }

            if (window.ZXing && window.ZXing.BrowserMultiFormatReader) {
                state.reader = new window.ZXing.BrowserMultiFormatReader();
                await state.reader.decodeFromConstraints(constraints, els.video, (result, err) => {
                    state.updateCount += 1;
                    if (result) {
                        addBarcode(result.getBarcodeFormat ? result.getBarcodeFormat().toString() : "", result.getText());
                    }
                    const { maxFrames } = getSettings();
                    if (state.updateCount >= maxFrames) {
                        stopScan(true);
                    }
                });
                setStatus("Сканирование запущено.");
                return;
            }

            setStatus("Сканирование не поддерживается браузером.", true);
            els.start.disabled = false;
            els.stop.disabled = true;
            state.scanning = false;
        } catch (err) {
            console.error(err);
            setStatus("Не удалось запустить камеру.", true);
            els.start.disabled = false;
            els.stop.disabled = true;
            state.scanning = false;
        }
    };

    const clearBarcodeFields = () => {
        els.barcodeStudentId.value = "";
        els.barcodeName1.value = "";
        els.barcodeName2.value = "";
        els.barcodeClass.value = "";
        els.barcodeCodes.forEach((input) => {
            input.value = "";
        });
    };

    const clearResultFields = () => {
        els.resultCode.value = "";
        els.resultScore.value = "";
    };

    if (!els.itiId) return;

    loadSettings();
    updateModeView();

    els.mode.addEventListener("change", () => {
        updateModeView();
        saveSettings();
    });

    [els.itiId, els.subjectId, els.login, els.password, els.maxFrames].forEach((input) => {
        input.addEventListener("input", saveSettings);
    });

    els.subjectLoad.addEventListener("click", fetchSubjectInfo);
    els.start.addEventListener("click", startScan);
    els.stop.addEventListener("click", () => stopScan(false));
    els.torch.addEventListener("click", toggleTorch);
    els.barcodeFetchStudent.addEventListener("click", () => {
        const studentId = parseInt(els.barcodeStudentId.value || "", 10);
        if (Number.isNaN(studentId)) {
            setStatus("Код школьника должен быть числом.", true);
            return;
        }
        fetchStudentInfo(studentId);
    });
    els.barcodeSave.addEventListener("click", saveBarcodes);
    els.barcodeClear.addEventListener("click", clearBarcodeFields);
    els.resultSave.addEventListener("click", saveResult);
    els.resultClear.addEventListener("click", clearResultFields);

    window.addEventListener("beforeunload", () => {
        stopStream();
    });
})();
