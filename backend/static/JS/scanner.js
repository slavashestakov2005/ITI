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
        debug: getEl("scanner-debug"),
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
        engine: null,
        ean8Counts: new Map(),
        ean13Counts: new Map(),
        updateCount: 0,
        lastScan: 0,
        detectedAny: false,
        studentFetchTimer: null,
        scanLoopId: null,
    };
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const setError = (text) => setStatus(text, true);

    const storageKey = "itiScannerSettings";

    const setStatus = (text, isError = false) => {
        els.status.textContent = text;
        els.status.style.color = isError ? "#a62727" : "#2f3b4e";
        els.status.style.background = isError ? "#ffe6e6" : "#f0f4fa";
    };
    const setDebug = (text) => {
        if (!els.debug) return;
        els.debug.textContent = text;
    };
    setDebug("JS загружен, ожидаю старт.");

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

    const pickVideoDeviceId = async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return null;
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videos = devices.filter((device) => device.kind === "videoinput");
            if (!videos.length) return null;
            const preferred = videos.find((device) => /back|rear|environment|wide/i.test(device.label));
            if (preferred) return preferred.deviceId;
            return videos[videos.length - 1].deviceId || null;
        } catch (err) {
            console.warn("Device enumeration failed", err);
            return null;
        }
    };

    const resetCounts = () => {
        state.ean8Counts.clear();
        state.ean13Counts.clear();
        state.updateCount = 0;
        state.detectedAny = false;
        state.lastScan = 0;
        setDebug("Сканирование не начато.");
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
        const isEan8 = normalizedFormat.includes("ean_8") || normalizedFormat.includes("ean8");
        const isEan13 = normalizedFormat.includes("ean_13") || normalizedFormat.includes("ean13");
        const byLength = digits.length === 8 || digits.length === 13;
        const guessEan8 = digits.length === 8;
        const guessEan13 = digits.length === 13;
        setDebug(`Последний код: ${digits} (${normalizedFormat || "unknown"})`);
        if (isEan8 || (!isEan13 && byLength && guessEan8)) {
            const val = parseInt(digits, 10);
            if (Number.isNaN(val)) return;
            const studentId = Math.floor(val / 10);
            updateCountMap(state.ean8Counts, studentId);
            state.detectedAny = true;
            if (getSettings().mode === "barcode") {
                els.barcodeStudentId.value = studentId;
                clearTimeout(state.studentFetchTimer);
                state.studentFetchTimer = setTimeout(() => {
                    fetchStudentInfo(studentId);
                }, 300);
            }
        }
        if (isEan13 || (!isEan8 && byLength && guessEan13)) {
            const val = parseInt(digits, 10);
            if (Number.isNaN(val)) return;
            updateCountMap(state.ean13Counts, val);
            state.detectedAny = true;
            if (getSettings().mode === "barcode") {
                const inputs = els.barcodeCodes;
                const existing = inputs.some((input) => input.value === String(val));
                if (!existing) {
                    const empty = inputs.find((input) => !input.value);
                    if (empty) empty.value = val;
                }
            } else {
                els.resultCode.value = val;
            }
            return;
        }
        if (!isEan8 && !isEan13) {
            if (getSettings().mode === "barcode") {
                const inputs = els.barcodeCodes;
                const existing = inputs.some((input) => input.value === digits);
                if (!existing) {
                    const empty = inputs.find((input) => !input.value);
                    if (empty) empty.value = digits;
                }
            } else {
                els.resultCode.value = digits;
            }
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
        if (codes.length) {
            els.barcodeCodes.forEach((input, index) => {
                if (codes[index]) input.value = codes[index];
            });
        }
        if (studentId) {
            await fetchStudentInfo(studentId);
        }
    };

    const fillResultFields = () => {
        const bestCode = getTopCode(state.ean13Counts);
        if (bestCode) {
            els.resultCode.value = bestCode;
        }
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
        state.engine = null;
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
        if (state.updateCount % 3 === 0) {
            setDebug(`Кадры: ${state.updateCount}, найдено: ${state.detectedAny ? "да" : "нет"}, режим: ${state.engine}`);
        }
        if (state.updateCount % 6 === 0) {
            const { maxFrames } = getSettings();
            setStatus(`Сканирование... кадр ${state.updateCount} из ${maxFrames}`);
        }
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
            if (!state.detectedAny && state.engine === "native" && window.ZXing) {
                setStatus("Не найдено, пробую другой режим...");
                stopStream();
                startScan("zxing");
                return;
            }
            await stopScan(true);
            return;
        }
        state.scanLoopId = requestAnimationFrame(scanLoop);
    };

    const startScan = async (forceEngine = null) => {
        if (state.scanning) return;
        resetCounts();
        setStatus("Запуск камеры...");
        els.start.disabled = true;
        els.stop.disabled = false;
        state.scanning = true;
        const baseVideoConstraints = {
            facingMode: { ideal: "environment" },
        };
        if (!isIOS) {
            baseVideoConstraints.width = { ideal: 1280 };
            baseVideoConstraints.height = { ideal: 720 };
            baseVideoConstraints.frameRate = { ideal: 30, max: 60 };
        }
        const baseConstraints = {
            video: baseVideoConstraints,
            audio: false,
        };
        const focusConstraints = {
            ...baseConstraints,
            video: {
                ...baseVideoConstraints,
                advanced: [{ focusMode: "continuous" }],
            },
        };

        try {
            let preferredDeviceId = null;
            if (forceEngine !== "zxing" && "BarcodeDetector" in window) {
                preferredDeviceId = await pickVideoDeviceId();
                if (preferredDeviceId) {
                    baseVideoConstraints.deviceId = { exact: preferredDeviceId };
                }
                try {
                    state.stream = await navigator.mediaDevices.getUserMedia(focusConstraints);
                } catch (err) {
                    state.stream = await navigator.mediaDevices.getUserMedia(baseConstraints);
                }
                els.video.srcObject = state.stream;
                state.track = state.stream.getVideoTracks()[0];
                await els.video.play();
                state.detector = new BarcodeDetector({
                    formats: ["ean_13", "ean_8", "code_128", "itf", "upc_a", "upc_e"],
                });
                state.engine = "native";
                setupTorch();
                setStatus("Сканирование запущено.");
                scanLoop();
                return;
            }

            if (window.ZXing && window.ZXing.BrowserMultiFormatReader) {
                const hints = new Map();
                hints.set(window.ZXing.DecodeHintType.POSSIBLE_FORMATS, [
                    window.ZXing.BarcodeFormat.EAN_13,
                    window.ZXing.BarcodeFormat.EAN_8,
                    window.ZXing.BarcodeFormat.CODE_128,
                    window.ZXing.BarcodeFormat.CODE_39,
                    window.ZXing.BarcodeFormat.ITF,
                    window.ZXing.BarcodeFormat.UPC_A,
                    window.ZXing.BarcodeFormat.UPC_E,
                ]);
                hints.set(window.ZXing.DecodeHintType.TRY_HARDER, true);
                hints.set(window.ZXing.DecodeHintType.ALSO_INVERTED, true);
                state.reader = new window.ZXing.BrowserMultiFormatReader(hints, 200);
                state.engine = "zxing";
                if (!preferredDeviceId) {
                    preferredDeviceId = await pickVideoDeviceId();
                }
                const decodeCallback = (result, err) => {
                    const now = performance.now();
                    if (now - state.lastScan < 150) {
                        return;
                    }
                    state.lastScan = now;
                    state.updateCount += 1;
                    if (state.updateCount % 3 === 0) {
                        setDebug(`Кадры: ${state.updateCount}, найдено: ${state.detectedAny ? "да" : "нет"}, режим: ${state.engine}`);
                    }
                    if (state.updateCount % 6 === 0) {
                        const { maxFrames } = getSettings();
                        setStatus(`Сканирование... кадр ${state.updateCount} из ${maxFrames}`);
                    }
                    if (result) {
                        addBarcode(result.getBarcodeFormat ? result.getBarcodeFormat().toString() : "", result.getText());
                    }
                    const { maxFrames } = getSettings();
                    if (state.updateCount >= maxFrames) {
                        if (!state.detectedAny && window.BarcodeDetector) {
                            setStatus("Не найдено, пробую другой режим...");
                            stopStream();
                            startScan("native");
                            return;
                        }
                        stopScan(true);
                    }
                };
                try {
                    if (isIOS) {
                        await state.reader.decodeFromVideoDevice(preferredDeviceId, els.video, decodeCallback);
                    } else {
                        await state.reader.decodeFromConstraints(focusConstraints, els.video, decodeCallback);
                    }
                } catch (err1) {
                    try {
                        await state.reader.decodeFromConstraints(baseConstraints, els.video, decodeCallback);
                    } catch (err2) {
                        try {
                            await state.reader.decodeFromVideoDevice(preferredDeviceId, els.video, decodeCallback);
                        } catch (err3) {
                            console.error(err1, err2, err3);
                            setError("Не удалось запустить сканер.");
                            await stopScan(false);
                            return;
                        }
                    }
                }
                setStatus("Сканирование запущено.");
                return;
            }

            setError("Сканирование не поддерживается браузером.");
            els.start.disabled = false;
            els.stop.disabled = true;
            state.scanning = false;
        } catch (err) {
            console.error(err);
            setError("Не удалось запустить камеру.");
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

    const params = new URLSearchParams(window.location.search);
    const itiParam = params.get("iti");
    const subjectParam = params.get("subject");
    const modeParam = params.get("mode");
    if (itiParam && !els.itiId.value) els.itiId.value = itiParam;
    if (subjectParam && !els.subjectId.value) els.subjectId.value = subjectParam;
    if (modeParam) els.mode.value = modeParam;
    if (subjectParam && !modeParam) els.mode.value = "result";
    updateModeView();
    saveSettings();
    if (subjectParam) {
        fetchSubjectInfo();
    }

    els.mode.addEventListener("change", () => {
        updateModeView();
        saveSettings();
    });

    [els.itiId, els.subjectId, els.login, els.password, els.maxFrames].forEach((input) => {
        input.addEventListener("input", saveSettings);
    });

    els.subjectLoad.addEventListener("click", fetchSubjectInfo);
    let subjectTimer = null;
    els.subjectId.addEventListener("input", () => {
        clearTimeout(subjectTimer);
        subjectTimer = setTimeout(fetchSubjectInfo, 500);
    });
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
