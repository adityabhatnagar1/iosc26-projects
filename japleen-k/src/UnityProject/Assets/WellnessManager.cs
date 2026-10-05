using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using TMPro;
using System;

public class WellnessManager : MonoBehaviour
{
    [Header("UI Elements")]
    public TMP_InputField urlInputField;   
    public TextMeshProUGUI statusText;     
    public TextMeshProUGUI timeSinceCheckInText; // UI text to display the live timer
    public GameObject scannerPanel;        
    public RawImage cameraDisplayArea;     
    public RectTransform scannerCanvasRect; 

    [Header("Runtime Settings")]
    private string serverUrl = "";         
    private string statusUrl = "";         
    private WebCamTexture camTexture;
    private bool isScanning = false;
    private DateTime serverLastCheckIn = DateTime.MinValue;

    private const string PrefsKey_ServerUrl = "SavedServerUrl";

    [System.Serializable]
    public class StatusResponse
    {
        public string last_check_in;
    }

    void Start()
    {
        if (scannerPanel != null) scannerPanel.SetActive(false);

        // Load saved URL on boot and fetch server status
        if (PlayerPrefs.HasKey(PrefsKey_ServerUrl))
        {
            string savedUrl = PlayerPrefs.GetString(PrefsKey_ServerUrl);
            SetServerUrl(savedUrl, false);
            if (urlInputField != null) urlInputField.text = savedUrl;
            
            StartCoroutine(FetchServerStatus());
        }
    }

    public void OpenScanner()
    {
        StartCoroutine(StartCameraAndScan());
    }

    IEnumerator StartCameraAndScan()
    {
        yield return Application.RequestUserAuthorization(UserAuthorization.WebCam);
        
        if (!Application.HasUserAuthorization(UserAuthorization.WebCam))
        {
            if (statusText) statusText.text = "Camera permission denied!";
            yield break;
        }

        scannerPanel.SetActive(true);
        
        camTexture = new WebCamTexture();
        cameraDisplayArea.texture = camTexture;
        camTexture.Play();
        isScanning = true;

        yield return new WaitForEndOfFrame();
        AdjustCameraDisplayOrientation();
    }

    void Update()
    {
        if (isScanning && camTexture != null && camTexture.isPlaying)
        {
            AdjustCameraDisplayOrientation();
        }

        UpdateCheckInTimerDisplay();
    }

    private void UpdateCheckInTimerDisplay()
    {
        if (timeSinceCheckInText == null) return;

        if (serverLastCheckIn == DateTime.MinValue)
        {
            timeSinceCheckInText.text = "00:00:00 (Syncing...)";
            return;
        }

        TimeSpan elapsed = DateTime.Now - serverLastCheckIn;
        if (elapsed.TotalSeconds < 0) elapsed = TimeSpan.Zero;

        timeSinceCheckInText.text = string.Format("{0:D2}:{1:D2}:{2:D2}", 
            (int)elapsed.TotalHours, 
            elapsed.Minutes, 
            elapsed.Seconds);
    }

    IEnumerator FetchServerStatus()
    {
        if (string.IsNullOrEmpty(statusUrl)) yield break;

        UnityWebRequest request = UnityWebRequest.Get(statusUrl);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            StatusResponse res = JsonUtility.FromJson<StatusResponse>(request.downloadHandler.text);
            if (DateTime.TryParse(res.last_check_in, out DateTime parsedTime))
            {
                serverLastCheckIn = parsedTime;
            }
        }
        else
        {
            Debug.LogWarning("Failed to fetch server status: " + request.error);
        }
    }

    private void AdjustCameraDisplayOrientation()
    {
        if (cameraDisplayArea == null || camTexture == null) return;

        int orientation = -camTexture.videoRotationAngle;
        cameraDisplayArea.rectTransform.localEulerAngles = new Vector3(0, 0, orientation);

        bool mirrored = camTexture.videoVerticallyMirrored;
        Vector3 scale = cameraDisplayArea.rectTransform.localScale;
        scale.y = mirrored ? -1f : 1f;
        cameraDisplayArea.rectTransform.localScale = scale;
    }

    public void CloseScanner()
    {
        isScanning = false;
        if (camTexture != null && camTexture.isPlaying)
        {
            camTexture.Stop();
        }
        if (scannerPanel != null) scannerPanel.SetActive(false);
    }

    public void ConfirmManualUrl()
    {
        if (urlInputField != null && !string.IsNullOrEmpty(urlInputField.text))
        {
            SetServerUrl(urlInputField.text.Trim(), true);
            StartCoroutine(FetchServerStatus());
        }
        else
        {
            if (statusText) statusText.text = "Please enter a valid URL!";
        }
    }

    private void SetServerUrl(string url, bool saveToPrefs)
    {
        string baseUrl = url.TrimEnd('/');
        if (baseUrl.EndsWith("/button"))
        {
            baseUrl = baseUrl.Substring(0, baseUrl.Length - 7);
        }

        serverUrl = baseUrl + "/button";
        statusUrl = baseUrl + "/status";
        
        if (saveToPrefs)
        {
            PlayerPrefs.SetString(PrefsKey_ServerUrl, serverUrl);
            PlayerPrefs.Save();
            Debug.Log("Server URL saved permanently: " + serverUrl);
        }

        if (statusText) statusText.text = "Connected: " + serverUrl;
    }

    public void OnCheckInButtonClicked()
    {
        if (string.IsNullOrEmpty(serverUrl))
        {
            if (statusText) statusText.text = "Please enter the server URL first!";
            return;
        }
        StartCoroutine(SendButtonPress("checkin"));
    }

    public void OnEmergencyButtonClicked()
    {
        if (string.IsNullOrEmpty(serverUrl))
        {
            if (statusText) statusText.text = "Please enter the server URL first!";
            return;
        }
        StartCoroutine(SendButtonPress("emergency"));
    }

    IEnumerator SendButtonPress(string type)
    {
        string jsonPayload = "{\"type\":\"" + type + "\", \"device\":\"Unity_App\"}";
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);

        UnityWebRequest request = new UnityWebRequest(serverUrl, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
            if (statusText) statusText.text = "Failed to reach server.";
        }
        else
        {
            Debug.Log("Successfully sent " + type + " signal.");
            
            if (type == "checkin")
            {
                StatusResponse res = JsonUtility.FromJson<StatusResponse>(request.downloadHandler.text);
                if (!string.IsNullOrEmpty(res.last_check_in) && DateTime.TryParse(res.last_check_in, out DateTime parsedTime))
                {
                    serverLastCheckIn = parsedTime;
                }
            }

            if (statusText) statusText.text = type.ToUpper() + " sent successfully!";
        }
    }
}