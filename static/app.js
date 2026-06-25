document.addEventListener('DOMContentLoaded', () => {
    const investigateBtn = document.getElementById('investigateBtn');
    const investigationSection = document.getElementById('investigationSection');
    const terminalBody = document.getElementById('terminalBody');
    const reportContainer = document.getElementById('reportContainer');
    const markdownBody = document.getElementById('markdownBody');
    const remediationContainer = document.getElementById('remediationContainer');
    const remediationLogs = document.getElementById('remediationLogs');
    const successBanner = document.getElementById('successBanner');

    function appendTerminalLog(message, type = 'system-msg') {
        const p = document.createElement('p');
        p.className = `log-line ${type}`;
        p.textContent = `> ${message}`;
        terminalBody.appendChild(p);
        terminalBody.scrollTop = terminalBody.scrollHeight;
    }

    async function simulateTypingLog(message, delay = 500) {
        return new Promise(resolve => {
            setTimeout(() => {
                appendTerminalLog(message, 'agent-msg');
                resolve();
            }, delay);
        });
    }

    investigateBtn.addEventListener('click', async () => {
        const incidentSelect = document.getElementById('incidentSelect');
        const alertMessage = incidentSelect ? incidentSelect.value : "checkout-service latency has spiked and payment authorizations are failing. Investigate immediately.";

        // UI updates
        investigateBtn.disabled = true;
        investigateBtn.textContent = 'Investigating...';
        investigationSection.classList.remove('hidden');
        
        // Simulate initial agent thought process
        await simulateTypingLog("Initializing LangGraph ReAct Agent with Gemini 2.5 Pro...", 800);
        await simulateTypingLog(`Analyzing incoming alert: '${alertMessage.substring(0, 40)}...'`, 1000);
        await simulateTypingLog("Invoking Tool: Get_Active_Alerts...", 1200);
        await simulateTypingLog("Invoking Tool: Get_Service_Architecture(checkout-service)...", 1000);
        await simulateTypingLog("Tracing dependency graph. Investigating payment-service...", 1500);
        await simulateTypingLog("Synthesizing final Incident Report...", 1000);

        try {
            // Actual API Call to backend
            const response = await fetch('/api/investigate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    alert_message: alertMessage
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                appendTerminalLog("[SYSTEM] Incident Report generated successfully.");
                
                // Render Markdown Report
                reportContainer.classList.remove('hidden');
                markdownBody.innerHTML = marked.parse(data.report);

                // Process Auto-Remediation Logs
                setTimeout(async () => {
                    remediationContainer.classList.remove('hidden');
                    
                    for (const log of data.remediation_logs) {
                        const li = document.createElement('li');
                        li.textContent = log;
                        if (log.includes("[SUCCESS]")) {
                            li.classList.add('success');
                        }
                        remediationLogs.appendChild(li);
                        
                        // Wait a bit between logs for visual effect
                        await new Promise(r => setTimeout(r, 600));
                    }

                    // Show success banner
                    setTimeout(() => {
                        successBanner.classList.remove('hidden');
                        investigateBtn.textContent = 'Incident Resolved';
                    }, 500);

                }, 1000);
            } else {
                appendTerminalLog(`[ERROR] ${data.detail}`, 'system-msg');
                investigateBtn.disabled = false;
                investigateBtn.textContent = 'Retry Investigation';
            }

        } catch (error) {
            appendTerminalLog(`[ERROR] Failed to reach API: ${error.message}`, 'system-msg');
            investigateBtn.disabled = false;
            investigateBtn.textContent = 'Retry Investigation';
        }
    });
});
