(() => {
    const getEl = (id) => document.getElementById(id);

    const els = {
        found: getEl("scanner-found"),
        mode: getEl("scanner-mode"),
        maxFrames: getEl("scanner-max-frames"),
        start: getEl("scanner-start"),
        stop: getEl("scanner-stop"),
        torch: getEl("scanner-torch"),
        status: getEl("scanner-status"),
        video: getEl("scanner-video"),
        html5Wrap: getEl("scanner-html5-wrap"),
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
        html5Scanner: null,
        html5Timer: null,
        zxingTimer: null,
        quaggaRunning: false,
        previewStream: null,
        itiId: "",
        subjectId: "",
    };
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const setError = (text) => setStatus(text, true);

    const storageKey = "itiScannerSettings";
    let quaggaScriptPromise = null;

    const setStatus = (text, isError = false) => {
        els.status.textContent = text;
        els.status.style.color = isError ? "#a62727" : "#2f3b4e";
        els.status.style.background = isError ? "#ffe6e6" : "#f0f4fa";
    };
    const setDebug = () => {};
    const toggleFound = (visible) => {
        if (!els.found) return;
        els.found.style.display = visible ? "block" : "none";
    };
    toggleFound(false);

    const ensurePreview = async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
        if (state.previewStream) {
            els.video.srcObject = state.previewStream;
            els.video.style.display = "block";
            els.video.play().catch(() => {});
            return;
        }
        const previewConstraints = {
            video: {
                facingMode: { ideal: "environment" },
                width: { ideal: 640 },
                height: { ideal: 360 },
            },
            audio: false,
        };
        try {
            state.previewStream = await navigator.mediaDevices.getUserMedia(previewConstraints);
            els.video.srcObject = state.previewStream;
            els.video.style.display = "block";
            await els.video.play();
        } catch (err) {
            console.warn("preview stream failed", err);
        }
    };

    const params = new URLSearchParams(window.location.search);
    state.itiId = params.get("iti") || "";
    state.subjectId = params.get("subject") || "";

    const loadQuagga = () => {
        if (window.Quagga) return Promise.resolve();
        if (quaggaScriptPromise) return quaggaScriptPromise;
        quaggaScriptPromise = new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://unpkg.com/quagga@0.12.1/dist/quagga.min.js";
            script.async = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("quagga load failed"));
            document.head.appendChild(script);
        });
        return quaggaScriptPromise;
    };

    const loadSettings = () => {
        const raw = localStorage.getItem(storageKey);
        if (!raw) return;
        try {
            const settings = JSON.parse(raw);
            if (settings.mode) els.mode.value = settings.mode;
            if (settings.maxFrames) els.maxFrames.value = settings.maxFrames;
        } catch (err) {
            console.warn("Scanner settings parse error", err);
        }
    };

    const saveSettings = () => {
        const settings = {
            mode: els.mode.value,
            maxFrames: els.maxFrames.value,
        };
        localStorage.setItem(storageKey, JSON.stringify(settings));
    };

    const getSettings = () => ({
        itiId: (state.itiId || "").trim(),
        subjectId: (state.subjectId || "").trim(),
        login: "",
        password: "",
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
        toggleFound(false);
    };

    const normalizeDigits = (value) => {
        if (!value) return "";
        return String(value).replace(/\D/g, "");
    };

    const isValidEan13 = (digits) => {
        if (!digits || digits.length !== 13) return false;
        const nums = digits.split("").map((d) => parseInt(d, 10));
        if (nums.some((n) => Number.isNaN(n))) return false;
        const check = nums.pop();
        const sum = nums
            .slice()
            .reverse()
            .reduce((acc, n, idx) => acc + n * (idx % 2 === 0 ? 3 : 1), 0);
        const calc = (10 - (sum % 10)) % 10;
        return calc === check;
    };

    const isValidEan8 = (digits) => {
        if (!digits || digits.length !== 8) return false;
        const nums = digits.split("").map((d) => parseInt(d, 10));
        if (nums.some((n) => Number.isNaN(n))) return false;
        const check = nums.pop();
        const sum = nums.reduce((acc, n, idx) => acc + n * (idx % 2 === 0 ? 3 : 1), 0);
        const calc = (10 - (sum % 10)) % 10;
        return calc === check;
    };

    const updateCountMap = (map, code) => {
        if (!code) return;
        map.set(code, (map.get(code) || 0) + 1);
    };

    const addBarcode = (format, rawValue) => {
        const digits = normalizeDigits(rawValue);
        if (!digits) return;
        const normalizedFormat = String(format || "").toLowerCase();
        const looksEan8 = digits.length === 8 || normalizedFormat.includes("ean_8") || normalizedFormat.includes("ean8");
        const looksEan13 =
            digits.length === 13 || normalizedFormat.includes("ean_13") || normalizedFormat.includes("ean13");
        const validEan8 = looksEan8 && isValidEan8(digits);
        const validEan13 = looksEan13 && isValidEan13(digits);
        toggleFound(validEan8 || validEan13);

        if (validEan8) {
            const studentId = parseInt(digits, 10);
            if (Number.isNaN(studentId)) return;
            updateCountMap(state.ean8Counts, studentId);
            state.detectedAny = true;
        }

        if (validEan13) {
            const val = parseInt(digits, 10);
            if (Number.isNaN(val)) return;
            updateCountMap(state.ean13Counts, val);
            state.detectedAny = true;
            if (getSettings().mode === "result") {
                // В режиме результатов подставляем сразу, но только валидный код
                els.resultCode.value = val;
            }
            return;
        }

        // Игнорируем все прочие форматы, чтобы не спамить ошибками
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
        const threshold = Math.max(2, Math.floor(state.updateCount * 0.25));
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
                input.value = codes[index] ? String(codes[index]) : "";
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
    };

    const postJson = async (url, data) => {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return response.json();
    };

    const fetchStudentInfo = async (studentId) => {
        const { itiId } = getSettings();
        if (!itiId) {
            setStatus("В URL нет iti.", true);
            return;
        }
        try {
            const data = await postJson(`/${itiId}/student_info`, {
                student_id: studentId,
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
        const { itiId } = getSettings();
        const studentId = (els.barcodeStudentId.value || "").trim();
        if (!itiId || !studentId) {
            setStatus("В URL нет iti или не указан код школьника.", true);
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
        const { itiId, subjectId } = getSettings();
        const code = (els.resultCode.value || "").trim();
        const result = (els.resultScore.value || "").trim();
        if (!itiId || !subjectId || !code || !result) {
            setStatus("В URL нет iti/subject или не заполнены код/результат.", true);
            return;
        }
        const payload = [[code, result.replace(",", ".")]];
        try {
            const data = await postJson(`/${itiId}/${subjectId}/save_results`, {
                data: JSON.stringify(payload),
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
        if (state.html5Scanner) {
            state.html5Scanner.stop().catch(() => {});
            state.html5Scanner.clear();
            state.html5Scanner = null;
        }
        if (state.html5Timer) {
            clearInterval(state.html5Timer);
            state.html5Timer = null;
        }
        if (state.zxingTimer) {
            clearInterval(state.zxingTimer);
            state.zxingTimer = null;
        }
        if (state.quaggaRunning && window.Quagga) {
            try {
                window.Quagga.stop();
                window.Quagga.offDetected();
                window.Quagga.offProcessed();
            } catch (err) {
                // ignore
            }
            state.quaggaRunning = false;
        }
        if (state.stream) {
            state.stream.getTracks().forEach((track) => track.stop());
            state.stream = null;
            state.track = null;
        }
        // восстановить превью, если оно есть
        if (state.previewStream) {
            els.video.srcObject = state.previewStream;
            els.video.style.display = "block";
            els.video.play().catch(() => {});
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
        ensurePreview();
        toggleFound(false);
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
            await stopScan(true);
            return;
        }
        state.scanLoopId = requestAnimationFrame(scanLoop);
    };

    const startScan = async (forceEngine = null) => {
        // Сброс прежнего запуска
        if (state.scanning) {
            if (state.scanLoopId) cancelAnimationFrame(state.scanLoopId);
            stopStream();
            state.scanning = false;
        }
        resetCounts();
        setStatus("Готов к сканированию.");
        els.start.disabled = true;
        els.stop.disabled = false;
        state.scanning = true;
        await ensurePreview();
        // На время реального сканирования освобождаем превью-поток, чтобы камера была доступна движкам
        if (state.previewStream) {
            state.previewStream.getTracks().forEach((track) => track.stop());
            state.previewStream = null;
        }

        const baseVideoConstraints = {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30, max: 60 },
        };
        const baseConstraints = { video: baseVideoConstraints, audio: false };
        const focusConstraints = {
            ...baseConstraints,
            video: {
                ...baseVideoConstraints,
                advanced: [{ focusMode: "continuous" }],
            },
        };

        const tryQuagga = async () => {
            try {
                await loadQuagga();
                if (!window.Quagga) return false;
                const quaggaTarget = document.getElementById("scanner-html5") || els.html5Wrap || els.video;
                // показываем контейнер под quagga и готовим превью
                if (els.html5Wrap) els.html5Wrap.style.display = "none";
                els.video.style.display = "block";
                state.engine = "quagga";
                const readers = [
                    "ean_reader",
                    "ean_8_reader",
                ];
                const constraints = {
                    facingMode: "environment",
                    width: { ideal: 960 },
                    height: { ideal: 720 },
                };
                await new Promise((resolve, reject) => {
                    window.Quagga.init(
                        {
                            inputStream: {
                                type: "LiveStream",
                                target: quaggaTarget,
                                constraints,
                            },
                            decoder: { readers },
                            locate: true,
                            frequency: 10,
                            numOfWorkers: 0,
                        },
                        (err) => {
                            if (err) reject(err);
                            else resolve();
                        }
                    );
                });
                window.Quagga.onDetected((result) => {
                    if (!result || !result.codeResult || !result.codeResult.code) return;
                    state.detectedAny = true;
                    addBarcode(result.codeResult.format || "quagga", result.codeResult.code);
                });
                state.quaggaRunning = true;
                try {
                    window.Quagga.start();
                    // привязываем активный трек к video, чтобы был явный превью-поток
                    const track = window.Quagga.CameraAccess && window.Quagga.CameraAccess.getActiveTrack
                        ? window.Quagga.CameraAccess.getActiveTrack()
                        : null;
                    if (track) {
                        const previewStream = new MediaStream([track]);
                        els.video.srcObject = previewStream;
                        await els.video.play();
                    }
                } catch (startErr) {
                    console.warn("quagga start failed", startErr);
                    setError("Quagga не смогла запустить камеру.");
                    return false;
                }
                state.html5Timer = setInterval(() => {
                    if (!state.scanning) return;
                    state.updateCount += 1;
                    if (state.updateCount % 3 === 0) {
                        setDebug(`Кадры: ${state.updateCount}, найдено: ${state.detectedAny ? "да" : "нет"}, режим: ${state.engine}`);
                    }
                    if (state.updateCount % 6 === 0) {
                        const { maxFrames } = getSettings();
                        setStatus(`Сканирование... кадр ${state.updateCount} из ${maxFrames}`);
                    }
                    const { maxFrames } = getSettings();
                    if (state.updateCount >= maxFrames) {
                        stopScan(true);
                    }
                }, 200);
                setStatus("Сканирование запущено.");
                return true;
            } catch (err) {
                console.warn("quagga init failed", err);
                setError("Не удалось запустить quagga: " + (err && err.message ? err.message : err));
                if (els.html5Wrap) els.html5Wrap.style.display = "none";
                return false;
            }
        };

        const tryNative = async () => {
            if (!("BarcodeDetector" in window)) return false;
            let preferredDeviceId = await pickVideoDeviceId();
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
            els.video.style.display = "block";
            if (els.html5Wrap) els.html5Wrap.style.display = "none";
            setupTorch();
            setStatus("Сканирование запущено.");
            scanLoop();
            return true;
        };

        const tryZxing = async () => {
            if (!window.ZXing || !window.ZXing.BrowserMultiFormatReader) return false;
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
            els.video.style.display = "block";
            if (els.html5Wrap) els.html5Wrap.style.display = "none";
            let preferredDeviceId = await pickVideoDeviceId();
            const zxingProgress = () => {
                if (!state.scanning) return;
                state.updateCount += 1;
                if (state.updateCount % 3 === 0) {
                    setDebug(`Кадры: ${state.updateCount}, найдено: ${state.detectedAny ? "да" : "нет"}, режим: ${state.engine}`);
                }
                if (state.updateCount % 6 === 0) {
                    const { maxFrames } = getSettings();
                    setStatus(`Сканирование... кадр ${state.updateCount} из ${maxFrames}`);
                }
                const { maxFrames } = getSettings();
                if (state.updateCount >= maxFrames) {
                    stopScan(true);
                }
            };
            state.zxingTimer = setInterval(zxingProgress, 200);
            const decodeCallback = (result) => {
                if (!state.scanning) return;
                const now = performance.now();
                if (result) {
                    if (now - state.lastScan < 150) return;
                    state.lastScan = now;
                    addBarcode(result.getBarcodeFormat ? result.getBarcodeFormat().toString() : "", result.getText());
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
                        return false;
                    }
                }
            }
            setStatus("Сканирование запущено.");
            return true;
        };

        try {
            // заранее открываем превью-поток, чтобы не было чёрного экрана
            try {
                state.previewStream = await navigator.mediaDevices.getUserMedia(baseConstraints);
                els.video.srcObject = state.previewStream;
                els.video.style.display = "block";
                await els.video.play();
            } catch (previewErr) {
                console.warn("preview stream failed", previewErr);
            }

            if (isIOS || forceEngine === "html5") {
                const okQuagga = await tryQuagga();
                if (okQuagga) return;
            }

            const okNative = await tryNative();
            if (okNative) return;

            const okZxing = await tryZxing();
            if (okZxing) return;

            // Last-resort retry native once more
            const okNative2 = await tryNative();
            if (okNative2) return;

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

    loadSettings();
    updateModeView();

    const subjectParam = params.get("subject");
    const modeParam = params.get("mode");
    if (modeParam) els.mode.value = modeParam;
    if (subjectParam && !modeParam) els.mode.value = "result";
    updateModeView();
    saveSettings();
    if (!state.itiId) {
        setStatus("Добавьте ?iti=... в адресной строке.", true);
    }
    if (els.resultPanel && els.resultPanel.style.display !== "none" && !state.subjectId) {
        setStatus("Для режима результатов нужен ?subject=...", true);
    }

    els.mode.addEventListener("change", () => {
        updateModeView();
        saveSettings();
    });

    [els.maxFrames].forEach((input) => {
        input.addEventListener("input", saveSettings);
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

    ensurePreview();

    window.addEventListener("beforeunload", () => {
        stopStream();
    });
})();
