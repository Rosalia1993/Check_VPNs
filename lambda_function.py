import json
import boto3
import datetime
import random
#Comentario 2

def lambda_handler(event, context):
    print(restart_tunnels())

def restart_tunnels():
    ec2_client = boto3.client('ec2')
    describe_vpn_response = ec2_client.describe_vpn_connections()
    #print("estado {}".format(describe_vpn_response))
    instance_id = describe_vpn_response['VpnConnections'][0]['VpnConnectionId']
    print("vpn_connection_id {}".format(instance_id))
    tunnels = describe_vpn_response['VpnConnections'][0]['VgwTelemetry']
    print("tunnels completo {}".format(tunnels))
    tunnels_down_list= []
    
    for tunnel in tunnels:
        del tunnel['LastStatusChange']
        if tunnel['Status'] == 'DOWN':
            tunnels_down_list.append({"Status": tunnel.get("Status", "unknown"), "remote_ip": tunnel.get("OutsideIpAddress", "unknown")})
    
    print("tunnels_down_list {}".format(tunnels_down_list))   
    #print(f"Region: {vpn_connection['Region']}")
    if len(tunnels_down_list) > 0:
        random_index = random.randrange(0,len(tunnels_down_list))
        print(f"tunel randon index {random_index}")
        
        #for tunel in tunnels_down_list:
        tunnel_state = tunnels_down_list[random_index]['Status']
        estado_VPN = get_status_vpn()
        
        if estado_VPN == 'available':
            if tunnel_state == 'DOWN':
                ec2_client = boto3.client('ec2')
                response = ec2_client.modify_vpn_tunnel_options(
                    VpnConnectionId=instance_id,
                    VpnTunnelOutsideIpAddress=tunnels_down_list[random_index]['remote_ip'],
                    TunnelOptions={
                        'DPDTimeoutAction': 'restart'
                    }
                ) 
                print(response)
                code = 200
                description = "Reinicio aplicado:  VPN:{}, Tunel: {}".format(instance_id,tunnels_down_list[random_index]['remote_ip'])
                print(description)
                
            elif tunnel_state == 'UP':
                code = 200
                description = f"Tunnel {tunel['remote_ip']} for {instance_id} esta UP, no se necesita ninguna accion."
                print(description)
            else:
                code =  400
                description = "Tunnel status is not UP or DOWN"
                print(description)
        else:
            code = 400 
            description = f'VPN state is not Available: {estado_VPN}'
            print(description)
        
        
    else:
        code = 400
        description = f'There is not a DOWN Tunel for {instance_id}'
        print(description)
    
    return {
            'statusCode': code,
            'body': json.dumps({
                'message': description
            })
        }
        

    
def get_status_vpn():
    ec2_client = boto3.client('ec2')
    describe_vpn_response = ec2_client.describe_vpn_connections()
    estado_VPN =  describe_vpn_response['VpnConnections'][0]['State']
    print("Estado_VPN  {}".format(estado_VPN))
    
    return estado_VPN
    

    
    
