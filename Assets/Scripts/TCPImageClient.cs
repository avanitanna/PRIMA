using UnityEngine;
using System.Threading;
using System.Net.Sockets;
using System.IO;
using System.Collections.Concurrent;
using UnityEngine.UI;

public class TCPImageClient : MonoBehaviour
{
    Thread m_NetworkThread;
    bool m_NetworkRunning;
    ConcurrentQueue<byte[]> dataQueue = new ConcurrentQueue<byte[]>();
    private void OnEnable()
    {
        m_NetworkRunning = true;
        m_NetworkThread = new Thread(NetworkThread);
        m_NetworkThread.Start();
        
    }
    private void OnDisable()
    {
        m_NetworkRunning = false;
        if (m_NetworkThread != null)
        {
            if (!m_NetworkThread.Join(100))
            {
                m_NetworkThread.Abort();
            }
        }
    }
    private void NetworkThread()
    {
        TcpClient client = new TcpClient();
        client.Connect("127.0.0.1", 1234);
        using (var stream = client.GetStream())
        {
            BinaryReader reader = new BinaryReader(stream);
            try
            {
                while (m_NetworkRunning && client.Connected && stream.CanRead)
                {
                    int length = reader.ReadInt32();
                    byte[] data = reader.ReadBytes(length);
                    dataQueue.Enqueue(data);
                }
            }
            catch
            {

            }
        }
    }

    //public Material mat;
    private Texture2D tex1 = null;
    private Texture2D tex2 = null;
    private Texture2D tex3 = null;
    private Texture2D tex4 = null;
    private Texture2D tex5 = null;
    public RawImage theImage1;
    public RawImage theImage2;
    public RawImage theImage3;
    public RawImage theImage4;
    public RawImage theImage5;
    private int counter = 0;
    void Update()
    {
        byte[] data;
        if (dataQueue.Count > 0 && dataQueue.TryDequeue(out data))
        {

            if (counter < 5)
            {
                if (counter == 0)
                {
                    if (tex1 == null)
                        tex1 = new Texture2D(1, 1);
                    tex1.LoadImage(data);
                    tex1.Apply();
                    theImage1.texture = tex1;
                }

                if (counter == 1)
                {
                    if (tex2 == null)
                        tex2 = new Texture2D(1, 1);
                    tex2.LoadImage(data);
                    tex2.Apply();
                    theImage2.texture = tex2;
                }

                if (counter == 2)
                {
                    if (tex3 == null)
                        tex3 = new Texture2D(1, 1);
                    tex3.LoadImage(data);
                    tex3.Apply();
                    theImage3.texture = tex3;
                }

                if (counter == 3)
                {
                    if (tex4 == null)
                        tex4 = new Texture2D(1, 1);
                    tex4.LoadImage(data);
                    tex4.Apply();
                    theImage4.texture = tex4;
                }

                if (counter == 4)
                {
                    if (tex5 == null)
                        tex5 = new Texture2D(1, 1);
                    tex5.LoadImage(data);
                    tex5.Apply();
                    theImage5.texture = tex5;
                }

                counter = counter + 1;
                if (counter == 5)
                    Debug.Log("Images Ready");
            }
            //mat.mainTexture = tex;
            /*
            if (dataQueue.Count % 5 == 1) 
                theImage1.texture = tex;
            else if (dataQueue.Count % 5 == 2) 
                theImage2.texture = tex;
            else if (dataQueue.Count % 5 == 3) 
                theImage3.texture = tex;
            else if (dataQueue.Count % 5 == 4) 
                theImage4.texture = tex;
            else
                theImage5.texture = tex;
        */
        }
    }
}