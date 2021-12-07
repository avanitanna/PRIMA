using System;
using System.Collections;
using System.Collections.Generic;
using Tobii.XR;
using UnityEngine;
using UnityEngine.UI; 

public class RunScotoma : MonoBehaviour
{
    [SerializeField] private Camera vrCamera; 
    [SerializeField] private Material scotomaShaderMaterial;
    [SerializeField] private float scotomaSize = 0.1f; 
    [SerializeField] private bool _smoothMove = true;
    [SerializeField] [Range(1, 30)] private int _smoothMoveSpeed = 7;

    [SerializeField] private Text displayText; 
    private Vector3 _lastGazeDirection;

    // private ComputeBuffer debugBuffer;
    //
    // private double[] debugReader = new double[1]; 
    
    private void OnRenderImage(RenderTexture src, RenderTexture dest)
    {
        var provider = TobiiXR.Internal.Provider;
        var eyeTrackingData = new TobiiXR_EyeTrackingData();
        provider.GetEyeTrackingDataLocal(eyeTrackingData);

        var interpolatedGazeDirection = Vector3.Lerp(_lastGazeDirection, eyeTrackingData.GazeRay.Direction, 
            _smoothMoveSpeed * Time.unscaledDeltaTime);
        var usedDirection = _smoothMove ? interpolatedGazeDirection.normalized : eyeTrackingData.GazeRay.Direction.normalized;
        _lastGazeDirection = usedDirection; 
        
        float aspectRatio = (float) src.height /  src.width;

        var screenPos = vrCamera.WorldToScreenPoint(vrCamera.transform.position + vrCamera.transform.rotation * usedDirection);
        Debug.Log(screenPos);
        Debug.Log(screenPos.y / src.height);
        Debug.Log(screenPos.x / src.width); 
        
        //var displayTextText = displayText.GetComponent<Text>();
        //displayTextText.text = (screenPos.y / src.height) + ", " + (screenPos.x/src.width);
        scotomaShaderMaterial.SetFloat("scotomaSize", scotomaSize);
        scotomaShaderMaterial.SetFloat("gazeY", screenPos.y/src.height);
        scotomaShaderMaterial.SetFloat("gazeX", screenPos.x/src.width);
        scotomaShaderMaterial.SetFloat("aspectRatio", aspectRatio); 
        
        RenderTexture temp = src; 
        Graphics.Blit(src, temp, scotomaShaderMaterial);
        Graphics.Blit(temp, dest);

        // debugBuffer.GetData(debugReader);
        // Debug.Log(debugReader[0]); 
    }

    // Start is called before the first frame update
    void Start()
    {
        vrCamera = gameObject.GetComponent<Camera>(); 
        
        // debugBuffer =
        //     new ComputeBuffer(1,
        //         System.Runtime.InteropServices.Marshal.SizeOf(typeof(double)), ComputeBufferType.Default);
        // Graphics.SetRandomWriteTarget(2, debugBuffer, true);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
