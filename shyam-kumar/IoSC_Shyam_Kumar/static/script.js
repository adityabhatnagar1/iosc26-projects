/**
 * Password Strength & Breach-Pattern Checker
 * Client-Side Controller & Real-Time Analyzer
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const passwordInput = document.getElementById('password-input');
    const toggleBtn = document.getElementById('toggle-visibility-btn');
    const eyeIcon = document.getElementById('eye-icon');
    const eyeOffIcon = document.getElementById('eye-off-icon');
    const clearBtn = document.getElementById('clear-input-btn');
    const copyBtn = document.getElementById('copy-password-btn');
    const copyLabel = document.getElementById('copy-label');
    const checkForm = document.getElementById('password-form');
    const toast = document.getElementById('toast');

    // Password Search Box & Hint Dialog Elements
    const inputBox = document.getElementById('input-box');
    const passwordHintDialog = document.getElementById('password-hint-dialog');
    const hintCloseBtn = document.getElementById('hint-close-btn');
    let hintDismissTimer = null;

    // Generator elements
    const genLengthSlider = document.getElementById('gen-length');
    const genLengthVal = document.getElementById('gen-length-val');
    const lengthDecBtn = document.getElementById('length-dec-btn');
    const lengthIncBtn = document.getElementById('length-inc-btn');
    const lengthSecurityBadge = document.getElementById('length-security-badge');
    const lengthBadgeText = document.getElementById('length-badge-text');
    const genUpper = document.getElementById('gen-upper');
    const genLower = document.getElementById('gen-lower');
    const genDigits = document.getElementById('gen-digits');
    const genSymbols = document.getElementById('gen-symbols');
    const generateBtn = document.getElementById('generate-btn');

    // Preset buttons
    const presetButtons = document.querySelectorAll('.preset-btn');

    // Results container elements
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    const statusBanner = document.getElementById('status-banner');
    const strengthBadge = document.getElementById('strength-badge');
    const entropyVal = document.getElementById('entropy-val');
    const breachPill = document.getElementById('breach-pill');
    const breachStatusText = document.getElementById('breach-status-text');
    const meterFill = document.getElementById('meter-fill');
    const strengthSummary = document.getElementById('strength-summary');

    // Breach Box
    const breachAlertBox = document.getElementById('breach-alert-box');
    const breachIcon = document.getElementById('breach-icon');
    const breachAlertTitle = document.getElementById('breach-alert-title');
    const breachDetails = document.getElementById('breach-details');

    // Formula & variables
    const formulaMath = document.getElementById('formula-math');
    const varLength = document.getElementById('var-length');
    const varPool = document.getElementById('var-pool');
    const varSpace = document.getElementById('var-space');
    const varEntropy = document.getElementById('var-entropy');

    // Character matrix
    const badgeLower = document.getElementById('badge-lower');
    const countLower = document.getElementById('count-lower');
    const badgeUpper = document.getElementById('badge-upper');
    const countUpper = document.getElementById('count-upper');
    const badgeDigit = document.getElementById('badge-digit');
    const countDigit = document.getElementById('count-digit');
    const badgeSymbol = document.getElementById('badge-symbol');
    const countSymbol = document.getElementById('count-symbol');

    // Crack times
    const timeOnline = document.getElementById('time-online');
    const timeGpu = document.getElementById('time-gpu');
    const timeSuper = document.getElementById('time-super');

    // Patterns & Recommendations
    const patternsCard = document.getElementById('patterns-card');
    const patternList = document.getElementById('pattern-list');
    const recommendationList = document.getElementById('recommendation-list');

    // Table rows
    const tableRows = {
        'Very Weak': document.getElementById('row-very-weak'),
        'Weak': document.getElementById('row-weak'),
        'Moderate': document.getElementById('row-moderate'),
        'Strong': document.getElementById('row-strong'),
        'Very Strong': document.getElementById('row-very-strong')
    };

    // Modal Elements
    const resultModal = document.getElementById('result-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalDoneBtn = document.getElementById('modal-done-btn');
    const modalScrollBtn = document.getElementById('modal-scroll-btn');
    const modalStrengthCard = document.getElementById('modal-strength-card');
    const modalStrengthBadge = document.getElementById('modal-strength-badge');
    const modalEntropyVal = document.getElementById('modal-entropy-val');
    const modalMeterFill = document.getElementById('modal-meter-fill');
    const modalStrengthSummary = document.getElementById('modal-strength-summary');
    const modalBreachBox = document.getElementById('modal-breach-box');
    const modalBreachIcon = document.getElementById('modal-breach-icon');
    const modalBreachTitle = document.getElementById('modal-breach-title');
    const modalBreachDesc = document.getElementById('modal-breach-desc');
    const modalStatLength = document.getElementById('modal-stat-length');
    const modalStatPool = document.getElementById('modal-stat-pool');
    const modalStatCrack = document.getElementById('modal-stat-crack');
    const modalPatternBox = document.getElementById('modal-pattern-box');
    const modalPatternText = document.getElementById('modal-pattern-text');

    let debounceTimer = null;
    let lastEvaluatedPassword = null;
    let lastEvaluatedData = null;

    // -------------------------------------------------------------
    // Real-Time Analysis via API
    // -------------------------------------------------------------
    async function evaluatePassword(pwd) {
        if (!pwd || pwd.length === 0) {
            emptyState.classList.remove('hidden');
            resultsContent.classList.add('hidden');
            clearBtn.classList.add('hidden');
            highlightTableRow(null);
            lastEvaluatedPassword = null;
            lastEvaluatedData = null;
            return null;
        }

        clearBtn.classList.remove('hidden');

        try {
            const response = await fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd })
            });

            if (!response.ok) throw new Error('API check failed');
            const data = await response.json();
            lastEvaluatedPassword = pwd;
            lastEvaluatedData = data;
            updateResultsUI(data);
            return data;
        } catch (err) {
            console.error('Error checking password:', err);
            return null;
        }
    }

    // -------------------------------------------------------------
    // Update Results UI
    // -------------------------------------------------------------
    function updateResultsUI(data) {
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        const { length, entropy, formula_math, char_analysis, strength, breach_info, patterns, crack_times, recommendations } = data;

        // Banner & Badge
        statusBanner.style.borderColor = strength.color;
        strengthBadge.className = `badge ${strength.badge_class}`;
        strengthBadge.textContent = strength.tier;
        entropyVal.textContent = entropy.toFixed(2);

        meterFill.style.width = `${strength.score_percent}%`;
        meterFill.style.backgroundColor = strength.color;
        strengthSummary.textContent = strength.summary;

        // Breach pill & box
        if (breach_info.in_breach_list) {
            breachPill.className = 'breach-pill flag-danger';
            breachStatusText.textContent = breach_info.status_text;

            breachAlertBox.className = 'breach-alert-box breach-danger';
            breachIcon.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>`;
            breachAlertTitle.textContent = '⚠ Compromised in Common / Leaked Dataset';
            breachDetails.textContent = breach_info.details;
        } else {
            breachPill.className = 'breach-pill flag-safe';
            breachStatusText.textContent = 'NO';

            breachAlertBox.className = 'breach-alert-box breach-safe';
            breachIcon.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>`;
            breachAlertTitle.textContent = '✓ Local Dataset Check Passed';
            breachDetails.textContent = breach_info.details;
        }

        // Formula
        formulaMath.textContent = formula_math;
        varLength.textContent = `${length} chars`;
        varPool.textContent = `${char_analysis.pool_size} characters (${char_analysis.pool_breakdown || 'none'})`;
        varSpace.textContent = `${crack_times.combinations_formula} combinations`;
        varEntropy.textContent = `${entropy.toFixed(2)} bits`;

        // Character Matrix
        updateBadge(badgeLower, countLower, char_analysis.has_lower, char_analysis.count_lower);
        updateBadge(badgeUpper, countUpper, char_analysis.has_upper, char_analysis.count_upper);
        updateBadge(badgeDigit, countDigit, char_analysis.has_digit, char_analysis.count_digit);
        updateBadge(badgeSymbol, countSymbol, char_analysis.has_symbol, char_analysis.count_symbol);

        // Crack Times
        timeOnline.textContent = crack_times.online;
        timeGpu.textContent = crack_times.fast_gpu;
        timeSuper.textContent = crack_times.supercomputer;

        // Patterns
        if (patterns && patterns.length > 0) {
            patternsCard.classList.remove('hidden');
            patternList.innerHTML = patterns.map(p => `
                <div class="pattern-item">
                    <span class="pattern-tag">${escapeHtml(p.type)}</span>
                    <span class="pattern-desc">${escapeHtml(p.desc)}</span>
                </div>
            `).join('');
        } else {
            patternsCard.classList.add('hidden');
            patternList.innerHTML = '';
        }

        // Recommendations
        if (recommendations && recommendations.length > 0) {
            recommendationList.innerHTML = recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('');
        } else {
            recommendationList.innerHTML = '<li>Password has strong entropy and is not in local breach files!</li>';
        }

        // Highlight Educational Table Row
        highlightTableRow(strength.tier);
    }

    function updateBadge(badgeEl, countEl, hasCategory, count) {
        if (!badgeEl || !countEl) return;
        countEl.textContent = count;
        const iconSpan = badgeEl.querySelector('.badge-icon');
        if (hasCategory) {
            badgeEl.classList.add('active');
            if (iconSpan) iconSpan.textContent = '✓';
        } else {
            badgeEl.classList.remove('active');
            if (iconSpan) iconSpan.textContent = '✗';
        }
    }

    function highlightTableRow(activeTier) {
        Object.keys(tableRows).forEach(tier => {
            const row = tableRows[tier];
            if (row) {
                if (tier === activeTier) {
                    row.classList.add('active-row');
                } else {
                    row.classList.remove('active-row');
                }
            }
        });
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function showToast(msg) {
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 2500);
    }

    // -------------------------------------------------------------
    // Popup Modal Functions
    // -------------------------------------------------------------
    function openResultModal(data, pwd) {
        if (!resultModal || !data) return;

        const { length, entropy, strength, breach_info, char_analysis, crack_times, patterns } = data;

        // Strength badge, meter & overview
        if (modalStrengthBadge) {
            modalStrengthBadge.className = `badge ${strength.badge_class}`;
            modalStrengthBadge.textContent = strength.tier;
        }
        if (modalEntropyVal) {
            modalEntropyVal.textContent = entropy.toFixed(2);
        }
        if (modalMeterFill) {
            modalMeterFill.style.width = `${strength.score_percent}%`;
            modalMeterFill.style.backgroundColor = strength.color;
        }
        if (modalStrengthSummary) {
            modalStrengthSummary.textContent = strength.summary;
        }
        if (modalStrengthCard) {
            modalStrengthCard.style.borderColor = strength.color;
            modalStrengthCard.style.boxShadow = `0 0 24px ${strength.color}33`;
        }

        // Breach info
        if (modalBreachBox && modalBreachTitle && modalBreachDesc && modalBreachIcon) {
            if (breach_info && breach_info.in_breach_list) {
                modalBreachBox.className = 'modal-breach-box breach-danger';
                modalBreachIcon.innerHTML = `
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>`;
                modalBreachTitle.textContent = '⚠ Compromised in Leaked Database!';
                modalBreachDesc.textContent = breach_info.details || 'Found in compromised password datasets.';
            } else {
                modalBreachBox.className = 'modal-breach-box breach-safe';
                modalBreachIcon.innerHTML = `
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        <polyline points="9 12 11 14 15 10"></polyline>
                    </svg>`;
                modalBreachTitle.textContent = '✔ Safe from Known Leaks';
                modalBreachDesc.textContent = 'No match found in 1,000,000+ local breached password database.';
            }
        }

        // Fast metrics
        if (modalStatLength) modalStatLength.textContent = `${length} chars`;
        if (modalStatPool) modalStatPool.textContent = `R = ${char_analysis ? char_analysis.pool_size : 0}`;
        if (modalStatCrack) {
            const gpuTime = crack_times ? (crack_times.gpu_rig || crack_times.online_attack || 'Instant') : 'Instant';
            modalStatCrack.textContent = gpuTime;
        }

        // Patterns & Predictability warning
        if (modalPatternBox && modalPatternText) {
            if (patterns && patterns.length > 0) {
                modalPatternBox.classList.remove('hidden');
                modalPatternText.textContent = patterns.map(p => `${p.type}: ${p.desc}`).join(' | ');
            } else {
                modalPatternBox.classList.add('hidden');
                modalPatternText.textContent = '';
            }
        }

        // Reveal modal
        resultModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeResultModal() {
        if (!resultModal) return;
        resultModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // -------------------------------------------------------------
    // Generated Password Callout Hint Functions
    // -------------------------------------------------------------
    function showPasswordHint() {
        if (!passwordHintDialog) return;
        passwordHintDialog.classList.remove('hidden');
        if (inputBox) inputBox.classList.add('input-glow-pulse');

        clearTimeout(hintDismissTimer);
        hintDismissTimer = setTimeout(() => {
            hidePasswordHint();
        }, 6000);
    }

    function hidePasswordHint() {
        if (!passwordHintDialog) return;
        passwordHintDialog.classList.add('hidden');
        if (inputBox) inputBox.classList.remove('input-glow-pulse');
        clearTimeout(hintDismissTimer);
    }

    if (hintCloseBtn) {
        hintCloseBtn.addEventListener('click', hidePasswordHint);
    }

    // -------------------------------------------------------------
    // Event Listeners: Input & Realtime Debounce
    // -------------------------------------------------------------
    passwordInput.addEventListener('input', (e) => {
        hidePasswordHint();
        clearTimeout(debounceTimer);
        const val = e.target.value;
        debounceTimer = setTimeout(() => {
            evaluatePassword(val);
        }, 120);
    });

    passwordInput.addEventListener('focus', () => {
        if (inputBox) inputBox.classList.remove('input-glow-pulse');
    });

    // Clear input
    clearBtn.addEventListener('click', () => {
        hidePasswordHint();
        passwordInput.value = '';
        passwordInput.focus();
        evaluatePassword('');
    });

    // Visibility toggle
    toggleBtn.addEventListener('click', () => {
        hidePasswordHint();
        const isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
        eyeIcon.classList.toggle('hidden', isPassword);
        eyeOffIcon.classList.toggle('hidden', !isPassword);
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', async () => {
        hidePasswordHint();
        const pwd = passwordInput.value;
        if (!pwd) {
            showToast('No password entered to copy');
            return;
        }

        try {
            await navigator.clipboard.writeText(pwd);
            copyLabel.textContent = 'Copied!';
            showToast('Password copied to clipboard!');
            setTimeout(() => {
                copyLabel.textContent = 'Copy';
            }, 2000);
        } catch (err) {
            // Fallback for older browsers
            passwordInput.select();
            document.execCommand('copy');
            copyLabel.textContent = 'Copied!';
            showToast('Password copied to clipboard!');
            setTimeout(() => {
                copyLabel.textContent = 'Copy';
            }, 2000);
        }
    });

    // Quick test preset chips
    presetButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const sample = btn.getAttribute('data-pw');
            if (sample) {
                passwordInput.value = sample;
                evaluatePassword(sample);
                passwordInput.focus();
                if (window.innerWidth <= 992) {
                    setTimeout(() => {
                        resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                }
            }
        });
    });

    // -------------------------------------------------------------
    // "Check Password" Button / Form Submission -> Popup Modal
    // -------------------------------------------------------------
    if (checkForm) {
        checkForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const pwd = passwordInput.value;

            if (!pwd || pwd.trim().length === 0) {
                showToast('Please enter a password first!');
                passwordInput.focus();
                passwordInput.classList.add('input-shake');
                setTimeout(() => passwordInput.classList.remove('input-shake'), 450);
                return;
            }

            const checkBtn = document.getElementById('check-btn');
            const origHtml = checkBtn.innerHTML;
            checkBtn.disabled = true;
            checkBtn.innerHTML = `
                <svg class="spinner-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="0.9"></path>
                </svg>
                <span>Analyzing...</span>
            `;

            try {
                let data = null;
                // If the user hasn't changed the password and we already evaluated it, reuse it
                if (lastEvaluatedData && lastEvaluatedPassword === pwd) {
                    data = lastEvaluatedData;
                } else {
                    data = await evaluatePassword(pwd);
                }

                if (data) {
                    openResultModal(data, pwd);
                } else {
                    showToast('Could not evaluate password');
                }
            } catch (err) {
                console.error('Error during check:', err);
                showToast('Error analyzing password');
            } finally {
                checkBtn.disabled = false;
                checkBtn.innerHTML = origHtml;
            }
        });
    }

    // Modal Interaction Listeners
    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeResultModal);
    if (modalDoneBtn) modalDoneBtn.addEventListener('click', closeResultModal);

    if (modalScrollBtn) {
        modalScrollBtn.addEventListener('click', () => {
            closeResultModal();
            setTimeout(() => {
                resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 150);
        });
    }

    if (resultModal) {
        resultModal.addEventListener('click', (e) => {
            if (e.target === resultModal) {
                closeResultModal();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && resultModal && !resultModal.classList.contains('hidden')) {
            closeResultModal();
        }
    });

    // -------------------------------------------------------------
    // Password Generator Length Control Center
    // -------------------------------------------------------------
    function setPasswordLength(val) {
        let num = parseInt(val, 10);
        if (isNaN(num)) num = 16;
        num = Math.max(8, Math.min(48, num));

        if (genLengthSlider) {
            genLengthSlider.value = num;
            const percent = ((num - 8) / (48 - 8)) * 100;
            genLengthSlider.style.background = `linear-gradient(to right, var(--color-primary) 0%, var(--color-primary) ${percent}%, rgba(255, 255, 255, 0.1) ${percent}%, rgba(255, 255, 255, 0.1) 100%)`;
        }

        if (genLengthVal) {
            genLengthVal.textContent = num;
        }

        // Live Security Badge & Rating Feedback
        if (lengthSecurityBadge && lengthBadgeText) {
            lengthSecurityBadge.className = 'length-security-badge';
            if (num < 12) {
                lengthSecurityBadge.classList.add('badge-weak');
                lengthBadgeText.textContent = 'Too Short (Weak)';
            } else if (num < 16) {
                lengthSecurityBadge.classList.add('badge-fair');
                lengthBadgeText.textContent = 'Fair (Basic)';
            } else if (num < 20) {
                lengthSecurityBadge.classList.add('badge-recommended');
                lengthBadgeText.textContent = 'Recommended ★';
            } else if (num < 28) {
                lengthSecurityBadge.classList.add('badge-strong');
                lengthBadgeText.textContent = 'Strong Protection';
            } else {
                lengthSecurityBadge.classList.add('badge-ultra');
                lengthBadgeText.textContent = 'Ultra Secure 🛡️';
            }
        }

        // Stepper button disabled bounds
        if (lengthDecBtn) lengthDecBtn.disabled = (num <= 8);
        if (lengthIncBtn) lengthIncBtn.disabled = (num >= 48);

        // Synchronize Quick Tap preset pills
        const pills = document.querySelectorAll('.len-pill');
        pills.forEach(pill => {
            const pLen = parseInt(pill.getAttribute('data-length'), 10);
            if (pLen === num) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });

        // Synchronize track tick marks
        const ticks = document.querySelectorAll('.tick-mark');
        ticks.forEach(tick => {
            const tVal = parseInt(tick.getAttribute('data-val'), 10);
            if (tVal === num) {
                tick.classList.add('active-mark');
            } else {
                tick.classList.remove('active-mark');
            }
        });
    }

    if (genLengthSlider) {
        genLengthSlider.addEventListener('input', (e) => {
            setPasswordLength(e.target.value);
        });
    }

    if (lengthDecBtn) {
        lengthDecBtn.addEventListener('click', () => {
            const current = parseInt(genLengthSlider ? genLengthSlider.value : 16, 10);
            setPasswordLength(current - 1);
        });
    }

    if (lengthIncBtn) {
        lengthIncBtn.addEventListener('click', () => {
            const current = parseInt(genLengthSlider ? genLengthSlider.value : 16, 10);
            setPasswordLength(current + 1);
        });
    }

    // Quick Tap Preset Pills Click
    document.querySelectorAll('.len-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const len = pill.getAttribute('data-length');
            if (len) setPasswordLength(len);
        });
    });

    // Slider Tick Marks Click
    document.querySelectorAll('.tick-mark').forEach(tick => {
        tick.addEventListener('click', () => {
            const val = tick.getAttribute('data-val');
            if (val) setPasswordLength(val);
        });
    });

    // Initialize initial state on load
    if (genLengthSlider) {
        setPasswordLength(genLengthSlider.value || 16);
    }

    // Generator Checkboxes Validation & Denial State
    const genCheckboxWarning = document.getElementById('gen-checkbox-warning');

    function checkGeneratorOptions() {
        const hasSelection = (genUpper && genUpper.checked) ||
                             (genLower && genLower.checked) ||
                             (genDigits && genDigits.checked) ||
                             (genSymbols && genSymbols.checked);

        if (!hasSelection) {
            if (genCheckboxWarning) genCheckboxWarning.classList.remove('hidden');
            if (generateBtn) {
                generateBtn.classList.add('btn-disabled');
                generateBtn.setAttribute('aria-disabled', 'true');
            }
        } else {
            if (genCheckboxWarning) genCheckboxWarning.classList.add('hidden');
            if (generateBtn) {
                generateBtn.classList.remove('btn-disabled');
                generateBtn.removeAttribute('aria-disabled');
            }
        }
        return hasSelection;
    }

    [genUpper, genLower, genDigits, genSymbols].forEach(cb => {
        if (cb) {
            cb.addEventListener('change', checkGeneratorOptions);
        }
    });

    // Run on startup
    checkGeneratorOptions();

    generateBtn.addEventListener('click', async () => {
        // Enforce block: Deny generation if all checkboxes are unchecked
        if (!checkGeneratorOptions()) {
            showToast('⚠️ Action Denied: Please select at least one character type (A-Z, a-z, 0-9, or !@#$)!');
            const toggles = document.querySelector('.gen-toggles');
            if (toggles) {
                toggles.classList.add('input-shake');
                setTimeout(() => toggles.classList.remove('input-shake'), 450);
            }
            if (genCheckboxWarning) {
                genCheckboxWarning.classList.remove('hidden');
            }
            return; // Completely stop execution - NO password generated!
        }

        const length = genLengthSlider.value;
        const upper = genUpper.checked;
        const lower = genLower.checked;
        const digits = genDigits.checked;
        const symbols = genSymbols.checked;

        try {
            const url = `/api/generate?length=${length}&upper=${upper}&lower=${lower}&digits=${digits}&symbols=${symbols}`;
            const res = await fetch(url);
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                showToast(errData.error || 'Password generation denied. Select at least one character set.');
                return;
            }
            const data = await res.json();
            if (!data.password) {
                showToast('Generation denied: No character sets selected.');
                return;
            }

            passwordInput.value = data.password;
            updateResultsUI(data.evaluation);
            clearBtn.classList.remove('hidden');

            // Scroll UP to the password search/input box
            const targetElement = passwordHintDialog || inputBox || passwordInput;
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Show "Your password is here" callout dialog & glowing pulse
            showPasswordHint();
            passwordInput.focus();

            showToast('New strong password generated!');
        } catch (err) {
            console.error('Failed to generate password:', err);
            showToast('Failed to generate password');
        }
    });

    // -------------------------------------------------------------
    // SOC Tactical Mode Navigation Tabs
    // -------------------------------------------------------------
    const navTabs = document.querySelectorAll('.soc-nav-tab');
    navTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.getAttribute('href');
            if (targetId && targetId.startsWith('#')) {
                const targetEl = document.querySelector(targetId);
                if (targetEl) {
                    e.preventDefault();
                    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // Check if initial password already provided on page load (e.g. from POST or reload)
    if (passwordInput.value) {
        evaluatePassword(passwordInput.value);
    }
});
