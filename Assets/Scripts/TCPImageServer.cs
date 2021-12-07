using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ImageStreamServer
{
    public class Client
    {
        public TcpClient client;
        public BinaryWriter writer;
        public Client(TcpClient aClient)
        {
            client = aClient;
            writer = new BinaryWriter(client.GetStream());
        }
        public bool SendImageData(byte[] aData)
        {
            if (!client.Connected)
                return false;
            writer.Write(aData.Length);
            writer.Write(aData);
            return true;
        }
    }


    class Program
    {
        TcpListener m_Server;
        bool m_ServerRunning;
        Thread m_ListenThread;

        bool m_Sending;
        Thread m_SendingThread;
        List<Client> m_Clients = new List<Client>();

        static void Main(string[] args)
        {
            var prg = new Program();
            prg.Run();
        }

        void ListenThread()
        {
            m_Server = new TcpListener(IPAddress.Any, 1234);
            m_Server.Start();
            m_ServerRunning = true;
            while (m_ServerRunning)
            {
                try
                {
                    var newClient = m_Server.AcceptTcpClient();
                    lock (m_Clients)
                    {
                        m_Clients.Add(new Client(newClient));
                    }
                }
                catch (Exception e)
                {
                    Console.Write(e.Message);
                }
            }
            lock(m_Clients)
            {
                foreach(var c in m_Clients)
                {
                    try
                    {
                        c.client.Close();
                    }
                    catch
                    {
                    }
                }
                m_Clients.Clear();
            }
        }

        class FileItem
        {
            public string name;
            public byte[] data;
        }

        void SendThread()
        {
            var folder = new DirectoryInfo("C:/Users/BionicVisionVR/Documents/apurv/PRIMA/Assets/percept1.2/");
            var fileNames = folder.GetFiles("*.png");
            var files = new List<FileItem>();
            foreach(var fn in fileNames)
            {
                files.Add(new FileItem
                {
                    data = File.ReadAllBytes(fn.FullName),
                    name = fn.FullName
                } );
            }
            m_Sending = true;
            Random r = new Random();
            while (m_Sending)
            {
                Thread.Sleep(1500);

                var file = files[r.Next(files.Count)];
                Console.WriteLine("Sending File: " + file.name);
                Client[] clients;
                lock(m_Clients)
                {
                    clients = m_Clients.ToArray();
                }
                foreach (var client in clients)
                {
                    bool success = false;
                    try
                    {
                        success = client.SendImageData(file.data);
                    }
                    catch
                    {
                        success = false;
                        client.client.Close();
                    }
                    finally
                    {
                        if (!success)
                        {
                            lock (m_Clients)
                            {
                                m_Clients.Remove(client);
                            }
                        }
                    }
                }
            }
        }

        private void Run()
        {
            m_ListenThread = new Thread(ListenThread);
            m_ListenThread.Start();

            m_SendingThread = new Thread(SendThread);
            m_SendingThread.Start();

            string line;
            while ((line = Console.ReadLine()) != "stop")
            {
                line = line.ToLower().Trim();
                if (line == "status")
                {
                    lock (m_Clients)
                    {
                        Console.WriteLine("Connected clients: " + m_Clients.Count);
                    }
                }
                else
                {
                    Console.WriteLine(line);
                }
            }
            m_Sending = false;
            m_ServerRunning = false;
            m_Server.Stop();
            m_ListenThread.Join();
            m_SendingThread.Join();
            Console.WriteLine("");
            Console.WriteLine("Press <Enter> to quit");
            Console.ReadLine();
        }
    }
}